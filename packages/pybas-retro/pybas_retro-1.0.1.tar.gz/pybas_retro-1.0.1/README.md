# PyBAS - Python BASIC Interpreter

![PyBAS](https://raw.githubusercontent.com/arfan/pybas/main/pybas.jpg)

A lightweight BASIC language interpreter written in Python that allows you to write and execute classic BASIC programs with modern convenience.

## Features

- ✅ **Variable Assignment** - Store and manipulate data with LET statements
- ✅ **Mathematical Operations** - Full arithmetic support (+, -, *, /, **)
- ✅ **String Operations** - String concatenation and manipulation
- ✅ **Output** - Display results with PRINT statements
- ✅ **Input** - Interactive user input with INPUT statements
- ✅ **Loop Control** - FOR loops with STEP support for iteration
- ✅ **Comments** - Document your code with single quote comments
- ✅ **Automatic Type Conversion** - Seamless handling of numbers and strings
- ✅ **Line-by-Line Execution** - Traditional BASIC line number programming
- ✅ **Nested Loops** - Support for loops within loops
- ✅ **Code Formatter** - Built-in pybasfmt tool for automatic code formatting and indentation
- ✅ **Interactive REPL** - GW-BASIC style interactive programming environment with pybasrepl

## Installation

### From PyPI (Recommended)

```bash
pip install pybas-retro
```

### From Source

```bash
git clone https://github.com/arfan/pybas.git
cd pybas
pip install .
```

### Requirements

- Python 3.6 or higher
- No additional dependencies

## Quick Start

After installation, you can use PyBAS from anywhere in your system:

```bash
# Run a BASIC program
pybas hello.pybas

# Start the interactive REPL
pybasrepl

# Format BASIC code
pybasfmt program.pybas
```

### Example Programs

Create a simple Hello World program:

```basic
10 PRINT "Hello, World!"
20 END
```

Save it as `hello.pybas` and run:

```bash
pybas hello.pybas
```

## Usage

### Command Line Tools

PyBAS provides three command-line tools:

#### pybas - BASIC Interpreter
```bash
pybas <program_file.pybas>
```

#### pybasrepl - Interactive REPL
```bash
pybasrepl
```

#### pybasfmt - Code Formatter
```bash
pybasfmt program.pybas              # Format in-place
pybasfmt program.pybas -o clean.pybas  # Format to new file
```

### Example

```bash
pybas hello.pybas
```

## Language Syntax

PyBAS supports a subset of classic BASIC language features. Every statement must begin with a line number.

### Program Structure

```basic
10 [STATEMENT]
20 [STATEMENT]
30 [STATEMENT]
...
[last_line] END
```

### Supported Statements

#### LET - Variable Assignment

Assigns values to variables.

**Syntax:**
```basic
LET variable = expression
```

**Examples:**
```basic
10 LET X = 5
20 LET NAME = "Hello"
30 LET Y = X + 10
40 LET RESULT = X * Y + 2
```

**Features:**
- Supports numeric and string variables
- Mathematical expressions in assignments
- Variable names can contain letters and numbers
- No need to declare variable types

#### PRINT - Output

Displays values, variables, and expressions.

**Syntax:**
```basic
PRINT expression
```

**Examples:**
```basic
10 PRINT "Hello, World!"
20 PRINT X
30 PRINT "The result is: " + str(RESULT)
40 PRINT X + Y
```

**Features:**
- Print strings, numbers, and variables
- String concatenation with `+`
- Use `str()` to convert numbers to strings for concatenation
- Supports complex expressions

#### INPUT - User Input

Gets input from the user and stores it in a variable.

**Syntax:**
```basic
INPUT variable
INPUT "prompt", variable
```

**Examples:**
```basic
10 INPUT NAME
20 INPUT "Enter your age: ", AGE
30 INPUT "Enter a number: ", NUM
```

**Features:**
- Automatic type detection (numbers vs strings)
- Optional prompt message
- Converts numeric input to integers or floats automatically
- String input remains as text

#### FOR - Loop Control

Creates loops that repeat a block of code a specified number of times.

**Syntax:**
```basic
FOR variable = start TO end
  [statements]
NEXT variable

FOR variable = start TO end STEP increment
  [statements]
NEXT variable
```

**Examples:**
```basic
10 FOR I = 1 TO 5
20   PRINT "Number: " + str(I)
30 NEXT I

40 FOR J = 10 TO 1 STEP -1
50   PRINT "Countdown: " + str(J)
60 NEXT J

70 FOR K = 2 TO 20 STEP 2
80   PRINT "Even number: " + str(K)
90 NEXT K
```

**Features:**
- Loop variable is automatically incremented
- Default STEP is 1 if not specified
- Supports negative STEP for counting backwards
- Can use variables and expressions for start, end, and step values
- Nested loops are supported
- NEXT can specify variable name for clarity (optional)

#### END - Program Termination

Ends the program execution.

**Syntax:**
```basic
END
```

**Example:**
```basic
100 END
```

#### Comments

Add comments to document your code.

**Syntax:**
```basic
' This is a comment (at the beginning of a line)
```

**Example:**
```basic
' This program calculates area
10 LET WIDTH = 5
20 LET HEIGHT = 10
```

**Note:** Comments must be on their own lines and start with a single quote.

### Data Types

PyBAS automatically handles different data types:

#### Numbers
- **Integers**: `42`, `-17`, `0`
- **Floats**: `3.14`, `-2.5`, `0.001`

#### Strings
- **Text**: `"Hello"`, `"Python BASIC"`, `"123abc"`
- Use double quotes to define string literals
- Concatenate strings with the `+` operator

### Mathematical Operations

| Operator | Description | Example |
|----------|-------------|---------|
| `+` | Addition | `5 + 3 = 8` |
| `-` | Subtraction | `10 - 4 = 6` |
| `*` | Multiplication | `6 * 7 = 42` |
| `/` | Division | `15 / 3 = 5.0` |
| `**` | Exponentiation | `2 ** 3 = 8` |

### String Operations

| Operation | Description | Example |
|-----------|-------------|---------|
| `+` | Concatenation | `"Hello" + " World" = "Hello World"` |
| `str()` | Convert to string | `str(42) = "42"` |

### Variable Rules

- Variable names can contain letters, numbers, and underscores
- Variables are case-sensitive (`NAME` and `name` are different)
- No need to declare variables before use
- Variables can hold different types of data

## Examples and Tutorials

### Example 1: Hello World

**File: hello.pybas**
```basic
10 REM Hello World - Your First PyBAS Program
20 PRINT "Hello, World!"
30 PRINT "Welcome to PyBAS - a GW-BASIC compatible interpreter!"
40 END
```

**Output:**
```
Hello, World!
Welcome to PyBAS - a GW-BASIC compatible interpreter!
Program finished.
```

### Example 2: Loops and Variables

**File: loop.pybas**
```basic
10 REM Loop Example - Demonstrates FOR loops and variables
20 PRINT "Counting from 1 to 5:"
30 FOR I = 1 TO 5
40   PRINT "Number " + str(I)
50 NEXT I
60 PRINT "Done counting!"
70 END
```

### Example 3: Interactive Program

**File: interactive.pybas**
```basic
10 REM Interactive Example - Shows INPUT and conditional logic
20 PRINT "What's your name?"
30 INPUT NAME
40 PRINT "Hello, " + NAME + "!"
50 PRINT "How old are you?"
60 INPUT AGE
70 IF AGE >= 18 GOTO 100
80 PRINT "You are young!"
90 GOTO 110
100 PRINT "You are an adult!"
110 PRINT "Nice to meet you, " + NAME + "!"
120 END
```

### More Examples

Over 30 additional examples are available in the `examples/` folder, including:

- **Games**: Number guessing games, interactive programs
- **Mathematics**: Calculators, multiplication tables, pyramids  
- **Loops**: Various FOR loop demonstrations with STEP
- **Error Testing**: Comprehensive error handling examples
- **Code Formatting**: Before/after formatting examples

See `examples/README.md` for a complete catalog with descriptions.

### Example 4: Calculator (from examples/)

**File: calculator.pybas**
```basic
10 PRINT "Simple Calculator"
20 INPUT "Enter first number: ", NUM1
30 INPUT "Enter second number: ", NUM2
40 LET SUM = NUM1 + NUM2
50 LET PRODUCT = NUM1 * NUM2
60 PRINT str(NUM1) + " + " + str(NUM2) + " = " + str(SUM)
70 PRINT str(NUM1) + " * " + str(NUM2) + " = " + str(PRODUCT)
80 END
```

**Sample Run:**
```
Simple Calculator
Enter first number: 15
Enter second number: 4
15.0 + 4.0 = 19.0
15.0 * 4.0 = 60.0
Program finished.
```

### Example 3: Personal Information

**File: info.pybas**
```basic
10 INPUT "Enter your name: ", NAME
20 INPUT "Enter your age: ", AGE
30 LET BIRTH_YEAR = 2025 - AGE
40 PRINT "Hello, " + NAME
50 PRINT "You were born around " + str(BIRTH_YEAR)
60 END
```

### Example 4: Mathematical Operations

**File: math_demo.pybas**
```basic
10 LET A = 25
20 LET B = 4
30 PRINT "A = " + str(A)
40 PRINT "B = " + str(B)
50 PRINT "Addition: " + str(A + B)
60 PRINT "Subtraction: " + str(A - B)
70 PRINT "Multiplication: " + str(A * B)
80 PRINT "Division: " + str(A / B)
90 PRINT "A squared: " + str(A ** 2)
100 END
```

### Example 5: Star Pyramid with Loops

**File: pyramid.pybas**
```basic
10 PRINT "Star Pyramid Generator"
20 INPUT "Enter pyramid height: ", HEIGHT
30 FOR ROW = 1 TO HEIGHT
40   LET SPACES = HEIGHT - ROW
50   LET STARS = 2 * ROW - 1
60   LET SPACE_STR = ""
70   FOR S = 1 TO SPACES
80     LET SPACE_STR = SPACE_STR + " "
90   NEXT S
100   LET STAR_STR = ""
110   FOR T = 1 TO STARS
120     LET STAR_STR = STAR_STR + "*"
130   NEXT T
140   PRINT SPACE_STR + STAR_STR
150 NEXT ROW
160 END
```

**Sample Output (height = 4):**
```
Star Pyramid Generator
Enter pyramid height: 4
   *
  ***
 *****
*******
Program finished.
```

### Example 6: Loop with STEP

**File: step_demo.pybas**
```basic
10 PRINT "Counting by 2s from 1 to 10:"
20 FOR I = 1 TO 10 STEP 2
30   PRINT str(I)
40 NEXT I
50 PRINT "Counting backwards from 5 to 1:"
60 FOR J = 5 TO 1 STEP -1
70   PRINT str(J)
80 NEXT J
90 END
```

### Step-by-Step Tutorial: Creating Your First Program

1. **Create a new file** with `.pybas` extension:
   ```bash
   touch my_program.pybas
   ```

2. **Write your program** with line numbers:
   ```basic
   10 PRINT "My first PyBAS program!"
   20 INPUT "What's your name? ", USERNAME
   30 PRINT "Nice to meet you, " + USERNAME + "!"
   40 END
   ```

3. **Save the file** and run it:
   ```bash
   ./pybas my_program.pybas
   ```

4. **Follow the prompts** and see your program in action!

### Programming Tips

- **Line Numbers**: Use increments of 10 (10, 20, 30...) to leave room for future additions
- **Variable Names**: Use descriptive names like `STUDENT_NAME` instead of `X`
- **String Conversion**: Always use `str()` when concatenating numbers with strings
- **Comments**: Document complex calculations or important steps
- **Testing**: Start with simple programs and gradually add complexity

## Included Sample Programs

The repository includes several example programs to help you get started:

| File | Description |
|------|-------------|
| `hello.pybas` | Basic variables and string operations |
| `calculator.pybas` | Interactive calculator with user input |
| `counter.pybas` | Variable manipulation and arithmetic |
| `input_demo.pybas` | Personal information program with INPUT |
| `guess_demo.pybas` | Simple guessing game setup |
| `math.pybas` | Mathematical operations demonstration |
| `pyramid.pybas` | Interactive star pyramid generator with loops |
| `simple_pyramid.pybas` | Simple star pyramid using nested loops |
| `loop_test.pybas` | Basic FOR loop demonstration |
| `step_test.pybas` | FOR loops with STEP functionality |
| `messy_clean.pybas` | Example of formatted code (before/after pybasfmt) |

**Run any example:**
```bash
./pybas hello.pybas
./pybas calculator.pybas
./pybas pyramid.pybas
./pybas step_test.pybas

# Format any program
./pybasfmt program.pybas
```

## Advanced Usage

### Code Formatting with pybasfmt

PyBAS includes a code formatter called `pybasfmt` that automatically formats and indents your PyBAS programs for better readability and consistency.

#### Features

- **Line Number Normalization**: Renumbers lines in consistent increments (default: 10, 20, 30...)
- **Automatic Indentation**: Properly indents FOR loops and nested structures
- **Statement Formatting**: Adds consistent spacing around operators and keywords
- **Preserves Functionality**: Maintains the exact behavior of your program

#### Usage

**Format a file in-place:**
```bash
./pybasfmt program.pybas
```

**Format to a new file:**
```bash
./pybasfmt program.pybas -o formatted_program.pybas
```

**Preview formatting without changing files:**
```bash
./pybasfmt program.pybas --dry-run
```

**Custom indentation:**
```bash
./pybasfmt program.pybas --indent 4  # Use 4 spaces instead of default 2
```

**Custom line numbering:**
```bash
./pybasfmt program.pybas --line-increment 5  # Use 5, 10, 15... instead of 10, 20, 30...
```

**Format multiple files:**
```bash
./pybasfmt *.pybas
```

#### Example: Before and After

**Before formatting:**
```basic
5 PRINT"Messy code"
15  LET X=5
35   FOR I=1TO 5
45 PRINT"Number: "+str(I)
50FOR J = 1 TO I
60PRINT"*"
70NEXT J
90 NEXT  I
100END
```

**After formatting:**
```basic
10 PRINT "Messy code"
20 LET X = 5
30 FOR I = 1 TO 5
40   PRINT "Number: "+str(I)
50   FOR J = 1 TO I
60     PRINT "*"
70   NEXT J
80 NEXT I
90 END
```

#### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `-o, --output FILE` | Output to specific file | Format in-place |
| `-i, --indent N` | Indentation spaces | 2 |
| `-l, --line-increment N` | Line number increment | 10 |
| `--dry-run` | Preview without writing | Write files |

### Interactive Programming with pybasrepl

PyBAS includes a GW-BASIC style REPL (Read-Eval-Print Loop) that provides an interactive programming environment similar to classic BASIC interpreters.

#### Starting the REPL

```bash
./pybasrepl
```

#### REPL Features

- **Line-by-Line Programming**: Enter program lines with line numbers
- **Immediate Execution**: Run programs with the RUN command
- **Program Management**: Save, load, and manage program files
- **AUTO Mode**: Automatic line numbering for faster programming
- **Line Editing**: Add, modify, or delete program lines
- **Classic Commands**: LIST, NEW, SAVE, LOAD, DIR, and more

#### Basic REPL Commands

| Command | Description | Example |
|---------|-------------|---------|
| `[number] [statement]` | Enter/modify program line | `10 PRINT "Hello"` |
| `[number]` | Delete program line | `10` (deletes line 10) |
| `LIST` | Show entire program | `LIST` |
| `LIST [line]` | Show specific line | `LIST 10` |
| `LIST [start]-[end]` | Show line range | `LIST 10-50` |
| `RUN` | Execute current program | `RUN` |
| `NEW` | Clear current program | `NEW` |
| `SAVE [filename]` | Save program to file | `SAVE myprog` |
| `LOAD [filename]` | Load program from file | `LOAD myprog` |
| `DIR` | List .pybas files | `DIR` |
| `AUTO [start] [incr]` | Auto line numbering | `AUTO 100 5` |
| `RENUM [start] [incr]` | Renumber lines | `RENUM 10 10` |
| `HELP` | Show help | `HELP` |
| `EXIT` or `QUIT` | Exit REPL | `EXIT` |

#### Example REPL Session

```
PyBAS REPL v1.0
GW-BASIC style interactive environment
Type HELP for available commands

> 10 PRINT "Hello, PyBAS!"
Line 10 entered
> 20 FOR I = 1 TO 3
Line 20 entered
> 30 PRINT "Count: " + str(I)
Line 30 entered
> 40 NEXT I
Line 40 entered
> 50 END
Line 50 entered
> LIST
10 PRINT "Hello, PyBAS!"
20 FOR I = 1 TO 3
30 PRINT "Count: " + str(I)
40 NEXT I
50 END
> RUN
Running program...
----------------------------------------
Hello, PyBAS!
Count: 1
Count: 2
Count: 3
Program finished.
----------------------------------------
> SAVE demo
Program saved as demo.pybas
[demo.pybas] > EXIT
Goodbye!
```

#### AUTO Mode for Faster Programming

AUTO mode automatically assigns line numbers, making programming faster:

```
> AUTO 100 10
AUTO mode ON - starting at 100, increment 10
100 PRINT "Using AUTO mode"
110 FOR I = 1 TO 5
120   PRINT "Number: " + str(I)
130 NEXT I
140 END
150 
AUTO mode OFF
> LIST
100 PRINT "Using AUTO mode"
110 FOR I = 1 TO 5
120   PRINT "Number: " + str(I)
130 NEXT I
140 END
```

#### Program Management

- **Save programs**: `SAVE filename` (automatically adds .pybas extension)
- **Load programs**: `LOAD filename` 
- **List files**: `DIR` shows all .pybas files in current directory
- **Clear memory**: `NEW` removes current program
- **Renumber**: `RENUM` reorganizes line numbers for better spacing

The REPL provides the classic BASIC programming experience with modern conveniences!

### Running Programs

**Method 1: Direct execution (recommended)**
```bash
./pybas program.pybas
```

**Method 2: Using Python interpreter**
```bash
python3 pybas program.pybas
```

**Method 3: Full path execution**
```bash
/path/to/pybas /path/to/program.pybas
```

### Command Line Options

Currently, PyBAS supports basic program execution. The syntax is:

```bash
./pybas <program_file>
```

**Arguments:**
- `<program_file>`: Required. Path to your `.pybas` program file

**Exit Codes:**
- `0`: Program executed successfully
- `1`: Error (missing file, syntax error, etc.)

### Error Handling

If you provide incorrect arguments:
```bash
./pybas
# Output: Usage: pybas program.pybas
```

If the program file doesn't exist:
```bash
./pybas nonexistent.pybas
# Output: FileNotFoundError: [Errno 2] No such file or directory: 'nonexistent.pybas'
```

## Troubleshooting

### Common Issues and Solutions

#### 1. "Unknown statement" Error

**Problem:** Getting "Unknown statement: [statement]" message

**Solutions:**
- Check that your line starts with a line number: `10 PRINT "Hello"`
- Verify statement syntax matches the supported commands (LET, PRINT, INPUT, END)
- Make sure there's a space between the line number and statement

**Example Error:**
```
Unknown statement: HELLO "World"
```
**Fix:**
```basic
10 PRINT "World"  # Use PRINT instead of HELLO
```

#### 2. Syntax Errors in Expressions

**Problem:** Errors when evaluating mathematical expressions

**Common Causes:**
- Missing quotes around strings: `PRINT Hello` should be `PRINT "Hello"`
- Mixing types without conversion: `"Age: " + 25` should be `"Age: " + str(25)`
- Invalid variable names or undefined variables

**Example Error:**
```basic
10 LET X = Y + 5  # Error if Y is not defined
```
**Fix:**
```basic
10 LET Y = 10
20 LET X = Y + 5
```

#### 3. File Permission Issues

**Problem:** "Permission denied" when running `./pybas`

**Solution:**
```bash
chmod +x pybas  # Make the file executable
```

#### 4. Input Type Issues

**Problem:** Unexpected behavior with INPUT statements

**Common Issues:**
- INPUT automatically converts numeric strings to numbers
- To force string input, the interpreter currently auto-detects type
- Empty input may cause issues

**Workaround:**
```basic
10 INPUT "Enter text: ", TEXT
20 PRINT "You entered: " + str(TEXT)  # Always convert to string for printing
```

#### 5. Line Number Conflicts

**Problem:** Program doesn't execute in expected order

**Solution:**
- Ensure line numbers are in ascending order
- Use increments of 10 to leave room for additions
- Check for duplicate line numbers

### Limitations

**Current Limitations:**
- No conditional statements (IF/THEN/ELSE)
- No WHILE loops (only FOR loops supported)
- No subroutines (GOSUB/RETURN)
- No arrays or complex data structures
- No file I/O operations
- No GOTO statements
- Limited error handling
- Comments must be on separate lines

**Planned Features:**
- Control flow statements
- Loop constructs
- Enhanced error messages
- More built-in functions

### Debugging Tips

1. **Start Simple**: Begin with basic PRINT statements to verify your logic
2. **Check Variables**: Use PRINT statements to display variable values
3. **Line Numbers**: Use consistent increments (10, 20, 30...)
4. **Test Incrementally**: Add one feature at a time
5. **Validate Input**: Be mindful of the automatic type conversion

**Example Debug Session:**
```basic
10 LET X = 5
15 PRINT "X is: " + str(X)  # Debug statement
20 LET Y = X * 2
25 PRINT "Y is: " + str(Y)  # Debug statement
30 PRINT "Final result: " + str(Y)
40 END
```

## Contributing

Contributions are welcome! Areas for improvement:

- Additional BASIC language features
- Better error handling and messages
- Performance optimizations
- More example programs
- Enhanced documentation

## License

This project is open source. Feel free to use, modify, and distribute.

## Version History

- **v1.0**: Initial release with basic LET, PRINT, INPUT, and END statements
- **v1.1**: Added INPUT functionality with prompts and automatic type conversion
- **v1.2**: Added FOR loop support with NEXT statements and STEP functionality
- **v1.3**: Added pybasfmt code formatter with automatic indentation and formatting
- **v1.4**: Added pybasrepl interactive REPL environment with AUTO, RENUM, and classic BASIC commands

---

**Happy Programming with PyBAS!** 🚀

For questions, issues, or suggestions, please create an issue in the repository.
