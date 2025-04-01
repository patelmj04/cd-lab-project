# SLR Parser Generator

A web-based tool for generating SLR parsing tables from context-free grammars. This application allows users to input a grammar and generates the corresponding SLR parsing table along with first/follow sets and the canonical collection of LR(0) items.

## Features

- Input a context-free grammar in standard notation
- Generate SLR parsing table
- Display canonical collection of LR(0) item sets

- Calculate and display FIRST and FOLLOW sets
- Show the augmented grammar
- Detect and report conflicts in the SLR parsing table
- Interactive web interface with responsive design

## How to Use

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the Flask application:
   ```
   python app.py
   ```
4. Open your browser and navigate to `http://localhost:5000`
5. Enter your grammar in the input field and click "Generate SLR Parsing Table"

## Grammar Format

The grammar should be formatted as follows:
- One production rule per line
- Non-terminals should start with uppercase letters
- Use `->` to separate the left and right sides of a production
- Use `|` to separate alternative right-hand sides
- Use `ε` or `epsilon` for the empty string

Example grammar:
```
E -> E + T | T
T -> T * F | F
F -> ( E ) | id
```

## Implementation Details

The implementation includes:
- Parsing the input grammar
- Augmenting the grammar with a new start symbol
- Computing FIRST and FOLLOW sets
- Constructing the canonical collection of LR(0) item sets
- Building the SLR parsing table

## Technical Stack

- Python 3.x
- Flask (Web framework)
- HTML5, CSS3, JavaScript

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

This tool was created as a compiler construction project to demonstrate the SLR parsing algorithm. #   c d - l a b - p r o j e c t 
 
 
