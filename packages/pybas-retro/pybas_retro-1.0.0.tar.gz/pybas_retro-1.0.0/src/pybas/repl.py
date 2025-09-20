#!/usr/bin/env python3
"""
PyBAS REPL (pybasrepl)
A GW-BASIC style interactive environment for PyBAS programming

Features:
- Line-by-line program entry
- LIST, RUN, NEW, SAVE, LOAD commands
- Direct statement execution
- Program editing and management
- Classic BASIC REPL experience
"""

import sys
import os
import re
from typing import Dict, List, Optional
from pathlib import Path

from .interpreter import BasicInterpreter
from .formatter import PyBASFormatter


class PyBASREPL:
    def __init__(self):
        self.program_lines: Dict[int, str] = {}
        self.current_filename: Optional[str] = None
        self.running = True
        self.auto_mode = False
        self.auto_start = 10
        self.auto_increment = 10
        self.auto_current = 10
        
    def print_banner(self):
        """Print the startup banner"""
        print("PyBAS REPL v1.0")
        print("GW-BASIC style interactive environment")
        print("Type HELP for available commands")
        print()
    
    def parse_input(self, user_input: str) -> tuple:
        """Parse user input and determine if it's a line number + statement or command"""
        user_input = user_input.strip()
        if not user_input:
            return "empty", None, None
            
        # Check if input starts with a number (program line)
        match = re.match(r'^(\d+)\s*(.*)', user_input)
        if match:
            line_num = int(match.group(1))
            statement = match.group(2).strip()
            return "program_line", line_num, statement
        else:
            # In AUTO mode, treat non-command input as program line
            if self.auto_mode and not user_input.upper().startswith(('LIST', 'RUN', 'NEW', 'SAVE', 'LOAD', 'DIR', 'HELP', 'EXIT', 'QUIT', 'AUTO', 'RENUM', 'FORMAT')):
                return "auto_line", self.auto_current, user_input
            
            # Direct command
            parts = user_input.split()
            command = parts[0].upper()
            args = parts[1:] if len(parts) > 1 else []
            return "command", command, args
    
    def handle_program_line(self, line_num: int, statement: str):
        """Handle a program line entry"""
        if statement:
            # Add or replace line
            self.program_lines[line_num] = statement
            print(f"Line {line_num} entered")
        else:
            # Delete line if no statement
            if line_num in self.program_lines:
                del self.program_lines[line_num]
                print(f"Line {line_num} deleted")
            else:
                print(f"Line {line_num} not found")
    
    def cmd_list(self, args: List[str]):
        """LIST command - show program lines"""
        if not self.program_lines:
            print("No program in memory")
            return
            
        # Parse range if provided
        start_line = None
        end_line = None
        
        if len(args) == 1:
            if '-' in args[0]:
                # Range like "10-50"
                parts = args[0].split('-')
                start_line = int(parts[0]) if parts[0] else None
                end_line = int(parts[1]) if parts[1] else None
            else:
                # Single line
                start_line = end_line = int(args[0])
        elif len(args) == 2:
            start_line = int(args[0])
            end_line = int(args[1])
        
        # Get sorted line numbers
        sorted_lines = sorted(self.program_lines.keys())
        
        # Filter by range if specified
        if start_line is not None:
            sorted_lines = [n for n in sorted_lines if n >= start_line]
        if end_line is not None:
            sorted_lines = [n for n in sorted_lines if n <= end_line]
        
        # Display lines
        for line_num in sorted_lines:
            print(f"{line_num} {self.program_lines[line_num]}")
    
    def cmd_run(self, args: List[str]):
        """RUN command - execute the current program"""
        if not self.program_lines:
            print("No program to run")
            return
        
        try:
            # Convert program to lines format expected by BasicInterpreter
            program_text = []
            for line_num in sorted(self.program_lines.keys()):
                program_text.append(f"{line_num} {self.program_lines[line_num]}")
            
            # Create and run interpreter
            interpreter = BasicInterpreter(program_text)
            
            print("Running program...")
            print("-" * 40)
            interpreter.run()
            print("-" * 40)
            
        except Exception as e:
            print(f"Runtime error: {e}")
    
    def cmd_new(self, args: List[str]):
        """NEW command - clear current program"""
        self.program_lines.clear()
        self.current_filename = None
        print("Program cleared")
    
    def cmd_save(self, args: List[str]):
        """SAVE command - save current program to file"""
        if not args:
            if self.current_filename:
                filename = self.current_filename
            else:
                print("No filename specified")
                return
        else:
            filename = args[0]
            if not filename.endswith('.pybas'):
                filename += '.pybas'
        
        if not self.program_lines:
            print("No program to save")
            return
        
        try:
            with open(filename, 'w') as f:
                for line_num in sorted(self.program_lines.keys()):
                    f.write(f"{line_num} {self.program_lines[line_num]}\n")
            
            self.current_filename = filename
            print(f"Program saved as {filename}")
            
        except Exception as e:
            print(f"Error saving file: {e}")
    
    def cmd_load(self, args: List[str]):
        """LOAD command - load program from file"""
        if not args:
            print("Filename required")
            return
        
        filename = args[0]
        if not filename.endswith('.pybas'):
            filename += '.pybas'
        
        try:
            if not os.path.exists(filename):
                print(f"File {filename} not found")
                return
            
            self.program_lines.clear()
            
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("'"):
                        match = re.match(r'^(\d+)\s+(.*)', line)
                        if match:
                            line_num = int(match.group(1))
                            statement = match.group(2)
                            self.program_lines[line_num] = statement
            
            self.current_filename = filename
            print(f"Program loaded from {filename}")
            
        except Exception as e:
            print(f"Error loading file: {e}")
    
    def cmd_dir(self, args: List[str]):
        """DIR command - list .pybas files in current directory"""
        try:
            pybas_files = [f for f in os.listdir('.') if f.endswith('.pybas')]
            if pybas_files:
                print("PyBAS files in current directory:")
                for filename in sorted(pybas_files):
                    size = os.path.getsize(filename)
                    print(f"  {filename:<20} {size:>8} bytes")
            else:
                print("No .pybas files found")
        except Exception as e:
            print(f"Error listing directory: {e}")
    
    def cmd_help(self, args: List[str]):
        """HELP command - show available commands"""
        print("PyBAS REPL Commands:")
        print()
        print("Program Editing:")
        print("  [number] [statement]  - Enter or modify program line")
        print("  [number]              - Delete program line")
        print("  LIST                  - Show entire program")
        print("  LIST [line]           - Show specific line")
        print("  LIST [start]-[end]    - Show range of lines")
        print()
        print("Program Management:")
        print("  RUN                   - Execute current program")
        print("  NEW                   - Clear current program")
        print("  SAVE [filename]       - Save program to file")
        print("  LOAD [filename]       - Load program from file")
        print()
        print("File Operations:")
        print("  DIR                   - List .pybas files")
        print()
        print("System:")
        print("  HELP                  - Show this help")
        print("  EXIT or QUIT          - Exit REPL")
        print()
    
    def cmd_exit(self, args: List[str]):
        """EXIT command - quit the REPL"""
        if self.program_lines and self.current_filename is None:
            response = input("Program not saved. Exit anyway? (y/n): ").strip().lower()
            if response not in ['y', 'yes']:
                return
        
        print("Goodbye!")
        self.running = False
    
    def execute_command(self, command: str, args: List[str]):
        """Execute a REPL command"""
        commands = {
            'LIST': self.cmd_list,
            'RUN': self.cmd_run,
            'NEW': self.cmd_new,
            'SAVE': self.cmd_save,
            'LOAD': self.cmd_load,
            'DIR': self.cmd_dir,
            'HELP': self.cmd_help,
            'EXIT': self.cmd_exit,
            'QUIT': self.cmd_exit,
        }
        
        if command in commands:
            commands[command](args)
        else:
            print(f"Unknown command: {command}")
            print("Type HELP for available commands")
    
    def run(self):
        """Main REPL loop"""
        self.print_banner()
        
        while self.running:
            try:
                # Show prompt
                if self.current_filename:
                    prompt = f"[{self.current_filename}] > "
                else:
                    prompt = "> "
                
                user_input = input(prompt).strip()
                
                if not user_input:
                    continue
                
                input_type, data1, data2 = self.parse_input(user_input)
                
                if input_type == "program_line":
                    self.handle_program_line(data1, data2)
                elif input_type == "command":
                    self.execute_command(data1, data2)
                
            except KeyboardInterrupt:
                print("\nUse EXIT or QUIT to leave the REPL")
            except EOFError:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")


def main():
    """Main entry point for the pybasrepl command"""
    if len(sys.argv) > 1:
        print("PyBAS REPL - Interactive mode")
        print("Usage: pybasrepl")
        print("No command line arguments needed")
        sys.exit(1)
    
    repl = PyBASREPL()
    repl.run()


if __name__ == "__main__":
    main()