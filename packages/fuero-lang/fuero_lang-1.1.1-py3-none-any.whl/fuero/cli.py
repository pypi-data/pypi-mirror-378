"""
command line interface for fuero
"""

import sys
import argparse
import os
from .core.lexer import Lexer
from .core.parser import Parser
from .core.interpreter import Interpreter


def run_file(filename):
    """run a fuero source file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # tokenize
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        
        # parse
        parser = Parser(tokens)
        ast = parser.parse()
        
        # interpret
        interpreter = Interpreter()
        interpreter.interpret(ast)
        
    except FileNotFoundError:
        print(f"error: file '{filename}' not found", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)


def run_repl():
    """run interactive repl mode"""
    print("fuero 1.1.1 interactive mode")
    print("type 'exit' or 'quit' to exit")
    
    interpreter = Interpreter()
    
    while True:
        try:
            line = input("fuero> ")
            
            if line.strip().lower() in ['exit', 'quit']:
                break
                
            if not line.strip():
                continue
            
            # tokenize
            lexer = Lexer(line)
            tokens = lexer.tokenize()
            
            # parse
            parser = Parser(tokens)
            ast = parser.parse()
            
            # interpret
            result = interpreter.interpret(ast)
            if result is not None:
                print(result)
                
        except KeyboardInterrupt:
            print("\nuse 'exit' or 'quit' to exit")
        except EOFError:
            break
        except Exception as e:
            print(f"error: {e}")


def main():
    """main entry point for fuero cli"""
    parser = argparse.ArgumentParser(
        description='fuero programming language',
        prog='fuero'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='available commands')
    
    # run command
    run_parser = subparsers.add_parser('run', help='run a fuero file')
    run_parser.add_argument('file', help='fuero source file to execute')
    
    # repl command
    subparsers.add_parser('repl', help='start interactive mode')
    
    # version
    parser.add_argument('-v', '--version', action='version', version='fuero 1.1.1')
    
    args = parser.parse_args()
    
    if args.command == 'run':
        run_file(args.file)
    elif args.command == 'repl':
        run_repl()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
