# SLR Parser Generator

A web-based tool for generating SLR parsing tables from context-free grammars. This application allows users to input a grammar and generates the corresponding SLR parsing table along with FIRST and FOLLOW sets and the canonical collection of LR(0) items.

![image](https://github.com/user-attachments/assets/2af9f96b-cf24-4af6-8aac-3fc2fcd36f4a)


## Features

- Input a context-free grammar in standard notation
- Generate the SLR parsing table
- Display the canonical collection of LR(0) item sets
- Calculate and display FIRST and FOLLOW sets
- Show the augmented grammar
- Detect and report conflicts in the SLR parsing table
- Interactive web interface with a responsive design

## How to Use

1. Clone this repository:
   ```sh
   git clone <https://github.com/Khanba22/cd-lab-project.git>
   cd <cd-lab-project>
   ```
2. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Run the Flask application:
   ```sh
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

- **Backend:** Python 3.x, Flask
- **Frontend:** HTML5, CSS3, JavaScript

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## Acknowledgements

This tool was created as a compiler construction project to demonstrate the SLR parsing algorithm.

