#!/usr/bin/env python3

import sys

class BasicInterpreter:
    def __init__(self, program_lines):
        self.program = {}
        self.vars = {}
        self.pc = None
        self.stack = []
        self.for_stack = []  # Stack for FOR loops

        # Load program into a dict {line_number: statement}
        for line in program_lines:
            line = line.strip()
            if not line or line.startswith("'"):  # allow comments
                continue
            num, stmt = line.split(" ", 1)
            self.program[int(num)] = stmt.strip()

        self.pc = min(self.program.keys())

    def safe_eval(self, expression, line_num=None):
        """Safely evaluate a Python expression with user-friendly error messages."""
        try:
            return eval(expression, {}, self.vars)
        except ZeroDivisionError:
            error_msg = f"Error on line {line_num}: Division by zero"
            print(error_msg)
            sys.exit(1)
        except NameError as e:
            var_name = str(e).split("'")[1] if "'" in str(e) else "unknown"
            error_msg = f"Error on line {line_num}: Variable '{var_name}' is not defined"
            print(error_msg)
            sys.exit(1)
        except SyntaxError:
            error_msg = f"Error on line {line_num}: Invalid expression syntax"
            print(error_msg)
            sys.exit(1)
        except ValueError as e:
            error_msg = f"Error on line {line_num}: Invalid value - {str(e)}"
            print(error_msg)
            sys.exit(1)
        except TypeError as e:
            error_msg = f"Error on line {line_num}: Type error - {str(e)}"
            print(error_msg)
            sys.exit(1)
        except Exception as e:
            error_msg = f"Error on line {line_num}: {str(e)}"
            print(error_msg)
            sys.exit(1)

    def handle_if_statement(self, stmt, stmt_upper):
        """Handle IF...GOTO statements with comparison operators"""
        try:
            # Parse IF condition GOTO target
            # Examples: IF X = 5 GOTO 100, IF A < B GOTO 50
            if "GOTO" not in stmt_upper:
                print(f"Error on line {self.pc}: IF statement missing GOTO")
                sys.exit(1)
            
            # Split on GOTO
            if_part, goto_part = stmt_upper.split("GOTO", 1)
            target_line = int(goto_part.strip())
            
            # Extract condition from IF part
            condition = if_part[2:].strip()  # Remove "IF"
            
            # Parse comparison operators
            operators = ["<=", ">=", "<>", "=", "<", ">"]
            condition_result = False
            
            for op in operators:
                if op in condition:
                    left, right = condition.split(op, 1)
                    left_val = self.safe_eval(left.strip(), self.pc)
                    right_val = self.safe_eval(right.strip(), self.pc)
                    
                    if op == "=":
                        condition_result = left_val == right_val
                    elif op == "<>":
                        condition_result = left_val != right_val
                    elif op == "<":
                        condition_result = left_val < right_val
                    elif op == ">":
                        condition_result = left_val > right_val
                    elif op == "<=":
                        condition_result = left_val <= right_val
                    elif op == ">=":
                        condition_result = left_val >= right_val
                    break
            else:
                print(f"Error on line {self.pc}: Invalid IF condition syntax")
                sys.exit(1)
            
            # If condition is true, GOTO target line
            if condition_result:
                if target_line in self.program:
                    return target_line
                else:
                    print(f"Error on line {self.pc}: GOTO target line {target_line} does not exist")
                    sys.exit(1)
            
            # If condition is false, continue to next line
            return None
            
        except (ValueError, IndexError) as e:
            print(f"Error on line {self.pc}: Invalid IF...GOTO syntax")
            sys.exit(1)

    def run(self):
        while self.pc in self.program:
            stmt = self.program[self.pc]
            next_pc = self.execute(stmt)
            if stmt.upper().startswith("END"):
                break

            # Use the returned PC or move to next line
            if next_pc is not None:
                self.pc = next_pc
            else:
                # Move to next line if not changed by GOTO/GOSUB
                next_lines = sorted([n for n in self.program if n > self.pc])
                self.pc = next_lines[0] if next_lines else None

    def execute(self, stmt):
        # Convert statement to uppercase for case-insensitive keyword matching
        stmt_upper = stmt.upper()
        
        if stmt_upper.startswith("GOTO"):
            # Example: GOTO 100
            try:
                target_line = int(stmt_upper.split()[1])
                if target_line in self.program:
                    return target_line
                else:
                    print(f"Error on line {self.pc}: GOTO target line {target_line} does not exist")
                    sys.exit(1)
            except (IndexError, ValueError):
                print(f"Error on line {self.pc}: Invalid GOTO syntax")
                sys.exit(1)
        
        elif stmt_upper.startswith("IF"):
            # Example: IF X = 5 GOTO 100
            # Example: IF X < 10 GOTO 200
            return self.handle_if_statement(stmt, stmt_upper)
        
        elif stmt_upper.startswith("LET"):
            # Example: LET A = 5
            _, expr = stmt.split(" ", 1)
            var, val = expr.split("=")
            self.vars[var.strip()] = self.safe_eval(val.strip(), self.pc)

        elif stmt_upper.startswith("PRINT"):
            _, expr = stmt.split(" ", 1)
            print(self.safe_eval(expr.strip(), self.pc))

        elif stmt_upper.startswith("INPUT"):
            # Example: INPUT "Enter your name: ", NAME
            _, expr = stmt.split(" ", 1)
            if "," in expr:
                prompt, var = expr.split(",", 1)
                prompt = prompt.strip().strip('"')
                var = var.strip()
                user_input = input(prompt)
                # Try to convert to number if possible, otherwise keep as string
                try:
                    self.vars[var] = float(user_input) if '.' in user_input else int(user_input)
                except ValueError:
                    self.vars[var] = user_input
            else:
                # Simple INPUT without prompt
                var = expr.strip()
                user_input = input()
                try:
                    self.vars[var] = float(user_input) if '.' in user_input else int(user_input)
                except ValueError:
                    self.vars[var] = user_input

        elif stmt_upper.startswith("FOR"):
            # Example: FOR I = 1 TO 10
            # Example: FOR I = 1 TO 10 STEP 2
            _, expr = stmt.split(" ", 1)
            parts = expr.split()
            var = parts[0]
            start_val = self.safe_eval(parts[2], self.pc)
            to_idx = next(i for i, part in enumerate(parts) if part.upper() == "TO")
            end_val = self.safe_eval(parts[to_idx + 1], self.pc)
            
            # Check for STEP
            step_val = 1
            step_indices = [i for i, part in enumerate(parts) if part.upper() == "STEP"]
            if step_indices:
                step_idx = step_indices[0]
                step_val = self.safe_eval(parts[step_idx + 1], self.pc)
            
            # Initialize loop variable
            self.vars[var] = start_val
            
            # Push loop info onto stack
            self.for_stack.append({
                'var': var,
                'end': end_val,
                'step': step_val,
                'line': self.pc
            })

        elif stmt_upper.startswith("NEXT"):
            # Example: NEXT I or just NEXT
            # Example: NEXT I or just NEXT
            if not self.for_stack:
                print("NEXT without FOR")
                return None
                
            loop_info = self.for_stack[-1]
            var = loop_info['var']
            
            # Check if variable specified and matches
            if len(stmt.split()) > 1:
                specified_var = stmt.split()[1]
                if specified_var != var:
                    print(f"NEXT {specified_var} doesn't match FOR {var}")
                    return None
            
            # Increment loop variable
            self.vars[var] += loop_info['step']
            
            # Check if loop should continue
            if ((loop_info['step'] > 0 and self.vars[var] <= loop_info['end']) or
                (loop_info['step'] < 0 and self.vars[var] >= loop_info['end'])):
                # Continue loop - jump back to line after FOR
                for_line = loop_info['line']
                next_lines = sorted([n for n in self.program if n > for_line])
                if next_lines:
                    return next_lines[0]
            else:
                # Exit loop
                self.for_stack.pop()

        elif stmt_upper.startswith("END"):
            print("Program finished.")

        elif stmt_upper.startswith("REM"):
            # Comment - do nothing
            pass

        else:
            print(f"Unknown statement: {stmt}")
            
        return None


def main():
    """Main entry point for the pybas command"""
    if len(sys.argv) < 2:
        print("Usage: pybas program.pybas")
        sys.exit(1)

    filename = sys.argv[1]
    with open(filename) as f:
        lines = f.readlines()

    interpreter = BasicInterpreter(lines)
    interpreter.run()


if __name__ == "__main__":
    main()