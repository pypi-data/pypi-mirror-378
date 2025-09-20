#!/usr/bin/env python3
"""
PyBAS Formatter (pybasfmt)
A code formatter for PyBAS programs that provides:
- Line number normalization
- Consistent spacing and indentation
- Proper formatting of FOR loops and nested structures
- Comment formatting
"""

import sys
import argparse
import re
from typing import List, Tuple, Dict

class PyBASFormatter:
    def __init__(self, indent_size: int = 2, line_increment: int = 10):
        self.indent_size = indent_size
        self.line_increment = line_increment
        self.nest_level = 0
        self.for_stack = []
        
    def parse_line(self, line: str) -> Tuple[int, str]:
        """Parse a line and return (line_number, statement)"""
        line = line.strip()
        if not line or line.startswith("'"):
            return None, line
            
        # More robust parsing - handle cases where there might be no space after line number
        match = re.match(r'^(\d+)\s*(.*)', line)
        if match:
            line_num = int(match.group(1))
            statement = match.group(2).strip()
            return line_num, statement
        else:
            return None, line
    
    def format_statement(self, statement: str) -> str:
        """Format a single statement with proper spacing"""
        if not statement:
            return statement
            
        # Handle different statement types (case-insensitive)
        stmt_upper = statement.upper()
        if stmt_upper.startswith("LET"):
            return self.format_let_statement(statement)
        elif stmt_upper.startswith("PRINT"):
            return self.format_print_statement(statement)
        elif stmt_upper.startswith("INPUT"):
            return self.format_input_statement(statement)
        elif stmt_upper.startswith("FOR"):
            return self.format_for_statement(statement)
        elif stmt_upper.startswith("NEXT"):
            return self.format_next_statement(statement)
        elif stmt_upper.startswith("END"):
            return "END"
        else:
            return statement
    
    def format_let_statement(self, statement: str) -> str:
        """Format LET statements with proper spacing around ="""
        # Extract the part after LET
        expr = statement[3:].strip()
        if "=" in expr:
            var, val = expr.split("=", 1)
            return f"LET {var.strip()} = {val.strip()}"
        return statement
    
    def format_print_statement(self, statement: str) -> str:
        """Format PRINT statements"""
        expr = statement[5:].strip()
        # Add space after PRINT if there isn't one before a quote
        if expr.startswith('"') and not statement[5:6] == ' ':
            return f"PRINT {expr}"
        return f"PRINT {expr}"
    
    def format_input_statement(self, statement: str) -> str:
        """Format INPUT statements"""
        expr = statement[5:].strip()
        if "," in expr:
            prompt, var = expr.split(",", 1)
            return f"INPUT {prompt.strip()}, {var.strip()}"
        else:
            return f"INPUT {expr}"
    
    def format_for_statement(self, statement: str) -> str:
        """Format FOR statements"""
        expr = statement[3:].strip()
        
        # Handle cases like "I=1TO 5" or "I = 1 TO 5" with case insensitive keywords
        # First normalize the spacing around = and TO/STEP
        expr = re.sub(r'\s*=\s*', ' = ', expr)
        expr = re.sub(r'\s*TO\s*', ' TO ', expr, flags=re.IGNORECASE)
        expr = re.sub(r'\s*STEP\s*', ' STEP ', expr, flags=re.IGNORECASE)
        
        parts = expr.split()
        
        # Find TO and STEP case-insensitively
        to_idx = None
        step_idx = None
        for i, part in enumerate(parts):
            if part.upper() == "TO":
                to_idx = i
            elif part.upper() == "STEP":
                step_idx = i
        
        if len(parts) >= 5 and parts[1] == "=" and to_idx is not None:
            var = parts[0]
            start = parts[2]
            end = parts[to_idx + 1]
            
            if step_idx is not None and step_idx < len(parts) - 1:
                step = parts[step_idx + 1]
                return f"FOR {var} = {start} TO {end} STEP {step}"
            else:
                return f"FOR {var} = {start} TO {end}"
        
        return f"FOR {expr}"
    
    def format_next_statement(self, statement: str) -> str:
        """Format NEXT statements"""
        parts = statement.split()
        if len(parts) > 1:
            return f"NEXT {parts[1]}"
        else:
            return "NEXT"
    
    def calculate_indentation(self, statement: str) -> int:
        """Calculate the indentation level for a statement"""
        stmt_upper = statement.upper()
        if stmt_upper.startswith("FOR"):
            current_indent = self.nest_level
            self.nest_level += 1
            self.for_stack.append(self.nest_level - 1)
            return current_indent
        elif stmt_upper.startswith("NEXT"):
            if self.for_stack:
                self.nest_level -= 1
                return self.for_stack.pop()
            return max(0, self.nest_level - 1)
        else:
            return self.nest_level
    
    def format_program(self, lines: List[str]) -> List[str]:
        """Format an entire PyBAS program"""
        formatted_lines = []
        statements = []
        comments = []
        
        # First pass: parse and collect statements and comments
        for line_idx, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            elif line.startswith("'"):
                comments.append((line_idx, line))
            else:
                line_num, statement = self.parse_line(line)
                if line_num is not None and statement:
                    statements.append((line_num, statement))
        
        # Sort statements by original line number
        statements.sort()
        
        # Reset indentation state
        self.nest_level = 0
        self.for_stack = []
        
        # Second pass: format statements with new line numbers and indentation
        new_line_num = self.line_increment
        
        for original_line_num, statement in statements:
            # Calculate indentation
            indent_level = self.calculate_indentation(statement)
            indent = " " * (indent_level * self.indent_size)
            
            # Format the statement
            formatted_statement = self.format_statement(statement)
            
            # Create the formatted line
            formatted_line = f"{new_line_num} {indent}{formatted_statement}"
            formatted_lines.append(formatted_line)
            
            new_line_num += self.line_increment
        
        return formatted_lines
    
    def format_file(self, input_file: str, output_file: str = None) -> None:
        """Format a PyBAS file"""
        try:
            with open(input_file, 'r') as f:
                lines = f.readlines()
            
            # Strip newlines and format
            lines = [line.rstrip('\n\r') for line in lines]
            formatted_lines = self.format_program(lines)
            
            # Write output
            output_content = '\n'.join(formatted_lines) + '\n'
            
            if output_file:
                with open(output_file, 'w') as f:
                    f.write(output_content)
                print(f"Formatted {input_file} -> {output_file}")
            else:
                # In-place formatting
                with open(input_file, 'w') as f:
                    f.write(output_content)
                print(f"Formatted {input_file} (in-place)")
                
        except FileNotFoundError:
            print(f"Error: File '{input_file}' not found")
            sys.exit(1)
        except Exception as e:
            print(f"Error formatting file: {e}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="PyBAS code formatter - Format and indent PyBAS programs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pybasfmt program.pybas              # Format in-place
  pybasfmt program.pybas -o clean.pybas  # Format to new file
  pybasfmt *.pybas                    # Format multiple files
  pybasfmt program.pybas --indent 4   # Use 4-space indentation
        """
    )
    
    parser.add_argument('files', nargs='+', help='PyBAS files to format')
    parser.add_argument('-o', '--output', help='Output file (for single file input)')
    parser.add_argument('-i', '--indent', type=int, default=2, 
                       help='Indentation size (default: 2)')
    parser.add_argument('-l', '--line-increment', type=int, default=10,
                       help='Line number increment (default: 10)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show formatted output without writing files')
    
    args = parser.parse_args()
    
    if args.output and len(args.files) > 1:
        print("Error: --output can only be used with a single input file")
        sys.exit(1)
    
    formatter = PyBASFormatter(
        indent_size=args.indent,
        line_increment=args.line_increment
    )
    
    for file_path in args.files:
        if args.dry_run:
            try:
                with open(file_path, 'r') as f:
                    lines = [line.rstrip('\n\r') for line in f.readlines()]
                formatted_lines = formatter.format_program(lines)
                print(f"\n--- Formatted {file_path} ---")
                for line in formatted_lines:
                    print(line)
                print("--- End ---\n")
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
        else:
            output_file = args.output if args.output and len(args.files) == 1 else None
            formatter.format_file(file_path, output_file)

if __name__ == "__main__":
    main()