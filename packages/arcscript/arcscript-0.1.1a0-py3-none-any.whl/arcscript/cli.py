from .transpiler import parse_file 
import sys

def main():
    if len(sys.argv) != 3:
        print("Incorrect usage.")
        print("Usage: arcscript input.arc output.js")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    try:
        parse_file(input_file, output_file)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
