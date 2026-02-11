from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFileDialog, QTextEdit, 
                             QMessageBox, QLineEdit, QGroupBox, QScrollArea)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pdf_generator import PDFGenerator


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pdf_generator = PDFGenerator()
        self.input_pdf_path = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Course Notes to Worksheet Generator")
        self.setGeometry(100, 100, 900, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Title
        title_label = QLabel("📚 Course Notes to Worksheet Generator")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Instructions
        instructions = QLabel(
            "Upload your course notes PDF, and this tool will extract all questions "
            "into a separate worksheet with spacing for answers."
        )
        instructions.setWordWrap(True)
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet("color: #666; padding: 10px;")
        main_layout.addWidget(instructions)
        
        # Upload section
        upload_group = QGroupBox("Step 1: Upload Course Notes PDF")
        upload_layout = QVBoxLayout()
        
        upload_btn_layout = QHBoxLayout()
        self.upload_button = QPushButton("📁 Select PDF File")
        self.upload_button.clicked.connect(self.upload_pdf)
        self.upload_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        upload_btn_layout.addWidget(self.upload_button)
        
        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("color: #666; padding: 5px;")
        upload_btn_layout.addWidget(self.file_label)
        upload_btn_layout.addStretch()
        
        upload_layout.addLayout(upload_btn_layout)
        upload_group.setLayout(upload_layout)
        main_layout.addWidget(upload_group)
        
        # Preview section
        preview_group = QGroupBox("Step 2: Preview Extracted Questions")
        preview_layout = QVBoxLayout()
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlaceholderText("Questions will appear here after uploading a PDF...")
        preview_layout.addWidget(self.preview_text)
        
        preview_group.setLayout(preview_layout)
        main_layout.addWidget(preview_group)
        
        # Output section
        output_group = QGroupBox("Step 3: Generate Worksheet")
        output_layout = QVBoxLayout()
        
        # Worksheet title input
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("Worksheet Title:"))
        self.title_input = QLineEdit("Math Worksheet")
        title_layout.addWidget(self.title_input)
        output_layout.addLayout(title_layout)
        
        # Generate button
        self.generate_button = QPushButton("📄 Generate Worksheet PDF")
        self.generate_button.clicked.connect(self.generate_worksheet)
        self.generate_button.setEnabled(False)
        self.generate_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 12px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        output_layout.addWidget(self.generate_button)
        
        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
    def upload_pdf(self):
        """Handle PDF file upload."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Course Notes PDF",
            "",
            "PDF Files (*.pdf)"
        )
        
        if file_path:
            self.input_pdf_path = file_path
            file_name = os.path.basename(file_path)
            self.file_label.setText(f"Selected: {file_name}")
            self.statusBar().showMessage("Extracting questions...")
            
            try:
                # Extract questions
                questions = self.pdf_generator.extract_questions_from_pdf(file_path)
                
                if questions:
                    # Display preview
                    preview_text = f"Found {len(questions)} questions:\n\n"
                    preview_text += "\n\n".join(questions)
                    self.preview_text.setText(preview_text)
                    
                    self.generate_button.setEnabled(True)
                    self.statusBar().showMessage(f"Successfully extracted {len(questions)} questions")
                    
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Successfully extracted {len(questions)} questions from the PDF!"
                    )
                else:
                    self.preview_text.setText("No questions found. Please check the PDF formatting.")
                    self.generate_button.setEnabled(False)
                    self.statusBar().showMessage("No questions found")
                    
                    QMessageBox.warning(
                        self,
                        "No Questions Found",
                        "No questions were found in the PDF. Please ensure the PDF has questions "
                        "formatted with numbering (e.g., 2.1.1., 2.1.2., etc.)"
                    )
                    
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Error extracting questions: {str(e)}"
                )
                self.statusBar().showMessage("Error extracting questions")
    
    def generate_worksheet(self):
        """Generate the worksheet PDF."""
        if not self.pdf_generator.questions:
            QMessageBox.warning(
                self,
                "No Questions",
                "Please upload a PDF first to extract questions."
            )
            return
        
        # Get output file path
        default_name = self.title_input.text().replace(" ", "_") + ".pdf"
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Worksheet PDF",
            default_name,
            "PDF Files (*.pdf)"
        )
        
        if output_path:
            try:
                self.statusBar().showMessage("Generating worksheet PDF (compiling LaTeX)...")
                
                # Show info about LaTeX compilation
                QMessageBox.information(
                    self,
                    "Generating PDF",
                    "The worksheet will be generated using LaTeX for proper mathematical notation.\n\n"
                    "This may take a few moments. Please wait...\n\n"
                    "Note: If this is your first time, you may need to install LaTeX:\n"
                    "macOS: brew install --cask basictex"
                )
                
                # Generate the PDF
                self.pdf_generator.generate_worksheet_pdf(
                    output_path,
                    title=self.title_input.text()
                )
                
                self.statusBar().showMessage("Worksheet generated successfully!")
                
                QMessageBox.information(
                    self,
                    "Success",
                    f"Worksheet PDF generated successfully!\n\n"
                    f"Saved to: {output_path}\n\n"
                    f"The PDF was generated using LaTeX for proper mathematical formatting."
                )
                
            except Exception as e:
                error_msg = str(e)
                if "pdflatex not found" in error_msg:
                    QMessageBox.critical(
                        self,
                        "LaTeX Not Found",
                        "LaTeX is required to generate PDFs with proper mathematical notation.\n\n"
                        "To install on macOS:\n"
                        "1. Install Homebrew (if not installed): https://brew.sh\n"
                        "2. Run: brew install --cask basictex\n"
                        "3. After installation, restart the application\n\n"
                        f"Full error: {error_msg}"
                    )
                else:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Error generating worksheet: {error_msg}"
                    )
                self.statusBar().showMessage("Error generating worksheet")