# Math Worksheet Generator

## Overview
The Math Worksheet Generator is a desktop application designed to create customizable math worksheets in PDF format. It features a user-friendly graphical interface that allows users to generate worksheets with various mathematical problems and formatting options.

## Features
- User-friendly GUI for easy interaction
- Ability to generate PDF documents with customizable math problems
- Modular design with reusable components for maintainability
- Formatting utilities to ensure proper layout and spacing in generated PDFs

## Project Structure
```
math-worksheet-generator
├── src
│   ├── main.py               # Entry point of the application
│   ├── pdf_generator.py      # Functions for generating PDF documents
│   ├── gui
│   │   ├── main_window.py    # Main window layout and logic
│   │   └── components.py      # Reusable GUI components
│   └── utils
│       └── formatting.py      # Utility functions for formatting
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation
```

## Installation
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/math-worksheet-generator.git
   ```
2. Navigate to the project directory:
   ```
   cd math-worksheet-generator
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
To run the application, execute the following command:
```
python src/main.py
```
This will launch the GUI, allowing you to create and customize your math worksheets.

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.