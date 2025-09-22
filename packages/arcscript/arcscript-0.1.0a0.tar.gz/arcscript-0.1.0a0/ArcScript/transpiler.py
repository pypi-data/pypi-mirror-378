from lark import Lark, Transformer, v_args
from lark.indenter import Indenter
from pathlib import Path


GRAMMAR = r'''
    ?start: (_NL* (statement))* _NL*

    statement: print | var_dec | func_def | for_in_loop | for_range_loop | if_block | while_block | grab_set | append | insert | style_block | event | expression  

    var_dec: NAME "=" expression

    print: "print" "(" [expression ("," expression)* ] ")"

    expression: atom ((OP | COMP_OP) atom)*
    atom: STRING | NUMBER | NAME | func_call | grab | grab_all | create

    grab: "grab" STRING property*
    grab_set: "grab" STRING property+ "=" expression
    grab_all: "grabAll" STRING
    property: NAME | NAME "(" [expression ("," expression)*] ")"
    style_block: (STRING | NAME) _NL [_INDENT (style_assignment _NL*)+ _DEDENT]
    style_assignment: NAME "=" expression 

    event: (STRING | NAME) (NAME) (NAME) _NL [_INDENT (statement _NL*)+ _DEDENT]

    condition_group: expression (REL_OP expression)*

    block_body: _INDENT (statement _NL*)+ _DEDENT
    
    if_block: "if" condition_group _NL block_body _NL? else_block?
    else_block: "else" _NL block_body
    while_block: "while" condition_group _NL block_body

    for_in_loop: "for" NAME "in" expression _NL block_body
    for_range_loop: "for" NAME "in" "[" expression ("," expression)* "]" _NL block_body

    func_def: DEF NAME param_list _NL block_body
    
    func_call: NAME "(" [expression ("," expression)*] ")"

    param_list: "(" [NAME ("," NAME)*] ")"

    create: "create" STRING
    append: "append" expression "to" expression
    insert: "insert" expression "before" expression "in" expression

    OP: "+" | "-" | "*" | "/" | "%"
    COMP_OP: "==" | "!=" | ">" | "<" | ">=" | "<="
    
    DEF.2: "def" | "fn" | "function"
    REL_OP.2: "and" | "or" | "not" | "is" | "True" | "False"
    
    _NL: (/\r?\n[ \t]*/ | SH_COMMENT)+

    %import common.CNAME -> NAME
    %import common.NUMBER
    %import common.ESCAPED_STRING -> STRING
    %import common.SH_COMMENT
    %import common.WS_INLINE
    %ignore WS_INLINE

    %declare _INDENT _DEDENT
'''

@v_args(inline=True)
class Converter(Transformer):
    def __init__(self):
        super().__init__()

    def NAME(self, token):
        return token.value

    def STRING(self, token):
        return token.value

    def NUMBER(self, token):
        return token.value
        
    def DEF(self, token):
        return token.value

    def OP(self, token):
        return token.value

    def COMP_OP(self, token):
        return token.value

    def REL_OP(self, token):
        m = {
            "and": "&&", 
            "or": "||", 
            "not": "!", 
            "is": "===",
            "True": "true", 
            "False": "false",
        }
        return m.get(token.value, token.value)

    def start(self, *statements):
        return "\n".join(filter(None, statements))

    def statement(self, stmt):
        return stmt

    def expression(self, *parts):
        return " ".join(map(str, parts))

    def atom(self, value):
        return value

    def var_dec(self, name, expression):
        return f"let {name} = {expression};"

    def print(self, *expressions):
        args = ", ".join(expressions)
        return f"console.log({args});"

    def param_list(self, *params):
        return ", ".join(params)

    def func_call(self, func_name, *args):
        arg_string = ", ".join(map(str, args))
        return f"{func_name}({arg_string})"

    def func_def(self, _, func_name, params, body):
        body_lines = body.strip().split('\n')
        
        if body_lines and body_lines[0]:
            last_statement = body_lines.pop().strip()
            processed_body = [line.strip()  for line in body_lines]
            processed_body.append(f"return {last_statement}")
            indented_body = "\n".join("    " + line for line in processed_body)
            return f"function {func_name}({params}) {{\n{indented_body}\n}}"
        else:
            return f"function {func_name}({params}) {{}}"

    def condition_group(self, *parts):
        return " ".join(map(str, parts))

    def block_body(self, *statements):
        indented_lines = ["    " + s for s in statements if s]
        return "\n".join(indented_lines)

    def if_block(self, condition, body, el = None):
        if el is None:
            return f"if ({condition}) {{\n{body}\n}}"
        else:
            return f"if ({condition}) {{\n{body}\n}}" + "\n" + el

    
    def else_block(self, body):
        val = "else {\n" + body + "\n}"
        return val

    def while_block(self, condition, body):
        return f"while ({condition}) {{\n{body}\n}}"

    def for_in_loop(self, iterator_var, iterable_expr, body):
        return f"for (let {iterator_var} of {iterable_expr}) {{\n{body}\n}}"

    def for_range_loop(self, iterator_var, *args):
        *range_args, body = args
        num_args = len(range_args)
        start, end, step, op, inc_dec = 0, 0, 1, "", ""

        if num_args == 1:
            start = 0
            end = range_args[0]
            op = "<"
            inc_dec = f"{iterator_var}++"
        elif num_args == 2:
            start = range_args[0]
            end = range_args[1]
            if int(start) < int(end):
                op = "<"
                inc_dec = f"{iterator_var}++"
            else:
                op = ">"
                inc_dec = f"{iterator_var}--"
        elif num_args == 3:
            start = range_args[0]
            end = range_args[1]
            step = range_args[2]
            if int(start) < int(end):
                op = "<"
                inc_dec = f"{iterator_var} += {step}"
            else:
                op = ">"
                inc_dec = f"{iterator_var} -= {step}"
        else:
            return f"// Invalid number of arguments for range loop: {len(range_args)}"
        return f"for (let {iterator_var} = {start}; {iterator_var} {op} {end}; {inc_dec}) {{\n{body}\n}}"

    def property(self, name, *expressions):
        if not expressions: return name
        args = ", ".join(expressions)
        return f'{name}({args})'

    def grab(self, selector, *properties):
        base = f'document.querySelector({selector})'
        if not properties: return base
        prop_string = ""
        for prop in properties:
            if prop == "html": prop = "innerHTML"
            elif prop == "text": prop = "innerText"
            prop_string += "." + prop
        return base + prop_string

    def grab_set(self, selector, *parts):
        *properties, expression = parts
        prop_string = ""
        for prop in properties:
            if prop == "html": prop = "innerHTML"
            elif prop == "text": prop = "innerText"
            prop_string += "." + prop
        return f'document.querySelector({selector}){prop_string} = {expression};'

    def grab_all(self, selector):
        return f'document.querySelectorAll({selector})'

    def style_block(self, selector, *assignments):
        if getattr(selector, "type", None) == "STRING":
            sel_expr = f'document.querySelector({selector})'
        else:
            sel_expr = selector
        lines = ""
        for assignment in assignments:
            lines += sel_expr + assignment + "\n"
        return lines

    def style_assignment(self, property_name, property_value):
        return f'.style.{property_name} = {property_value}'
    
    def event(self, selector, event_name, handler=None, *assignments):

        if selector[0] == '"' and selector[-1] == '"':
            if not hasattr(self, "_event_counter"):
                self._event_counter = 0
            self._event_counter += 1
            varname = f"__event_selector_{self._event_counter}"
        
            assign = varname + f" = document.querySelector({selector})\n"
            if handler == "event":
                a = "{\n" + ''.join(list(assignments)) + "}"

                return (assign + f"{varname}.addEventListener('{event_name}', ({handler}) => {a})")
            else:
                return (assign + f"{varname}.addEventListener('{event_name}', {handler})")

        else:
            if handler == "event":
                a = "{\n" + ''.join(list(assignments)) + "}"

                return (f"{selector}.addEventListener('{event_name}', ({handler}) => {a})")
            else:
                return (f"{selector}.addEventListener('{event_name}', {handler})")
 

    def create(self, tag):
        return f"document.createElement({tag})"

    def append(self, child, parent):
        return f"{parent}.appendChild({child})"

    def insert(self, child, ref, parent):
        return f"{parent}.insertBefore({child}, {ref})"


class Indent(Indenter):
    NL_type = '_NL'
    OPEN_PAREN_types = []
    CLOSE_PAREN_types = []
    INDENT_type = '_INDENT'
    DEDENT_type = '_DEDENT'
    tab_len = 4


def parse_file(input_file, output_file):
    file_text = Path(input_file).read_text()
    parser = Lark(GRAMMAR, parser="lalr", postlex=Indent(), debug=True)
    transformer = Converter()

    lines = file_text.splitlines()
    js = ""
    arc = ""

    for line in lines:
        if line == "[JS]":
            for l in lines:
                if l == "[ARC]":
                    break
                if l == "[JS]":
                    continue

                js = js + l + "\n"

        if line == "[ARC]":
            for l in lines[lines.index(line) + 1:]:
                arc = arc + l + "\n"
    
    if not arc and not js:
        arc = file_text
    

    tree = parser.parse(arc)
    out_text = js + transformer.transform(tree)
    Path(output_file).write_text(out_text)
    print(f"Transpiled {input_file} -> {output_file}.")

