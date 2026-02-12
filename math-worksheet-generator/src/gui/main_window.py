from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QDragEnterEvent, QDropEvent
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pdf_generator import PDFGenerator


class DropArea(QWidget):
    """Drag and drop area for PDF files."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setAcceptDrops(True)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Upload icon (using emoji)
        icon_label = QLabel("📁")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 64px;")
        layout.addWidget(icon_label)
        
        # Main text
        text_label = QLabel("Drag files to upload")
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setStyleSheet("font-size: 20px; font-weight: 600; color: #1a1a1a;")
        layout.addWidget(text_label)
        
        # Or text
        or_label = QLabel("or")
        or_label.setAlignment(Qt.AlignCenter)
        or_label.setStyleSheet("font-size: 14px; color: #999;")
        layout.addWidget(or_label)
        
        # Browse button
        self.browse_btn = QPushButton("Browse Files")
        self.browse_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border: none;
                border-radius: 20px;
                padding: 10px 30px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
            QPushButton:pressed {
                background-color: #2D6BA3;
            }
        """)
        self.browse_btn.setCursor(Qt.PointingHandCursor)
        self.browse_btn.clicked.connect(self.parent_window.browse_file)
        layout.addWidget(self.browse_btn, alignment=Qt.AlignCenter)
        
        # Supported formats
        formats_label = QLabel("Supported formats: PDF")
        formats_label.setAlignment(Qt.AlignCenter)
        formats_label.setStyleSheet("font-size: 12px; color: #999; margin-top: 10px;")
        layout.addWidget(formats_label)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # Styling
        self.setStyleSheet("""
            DropArea {
                background-color: white;
                border: 2px dashed #d0d0d0;
                border-radius: 10px;
            }
        """)
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                DropArea {
                    background-color: #f0f8ff;
                    border: 2px dashed #4A90E2;
                    border-radius: 10px;
                }
            """)
    
    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            DropArea {
                background-color: white;
                border: 2px dashed #d0d0d0;
                border-radius: 10px;
            }
        """)
    
    def dropEvent(self, event: QDropEvent):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files and files[0].lower().endswith('.pdf'):
            self.parent_window.process_file(files[0])
        self.setStyleSheet("""
            DropArea {
                background-color: white;
                border: 2px dashed #d0d0d0;
                border-radius: 10px;
            }
        """)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pdf_generator = PDFGenerator()
        self.input_pdf_path = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Worksheet Generator")
        self.setGeometry(100, 100, 700, 600)
        
        # Set window background
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #00d4ff, stop:1 #4a90e2);
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        central_widget.setLayout(main_layout)
        
        # Title
        title_label = QLabel("Upload Files")
        title_font = QFont()
        title_font.setPointSize(28)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignLeft)
        title_label.setStyleSheet("color: white; margin-bottom: 20px;")
        main_layout.addWidget(title_label)
        
        # Drop area container
        drop_container = QWidget()
        drop_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 15px;
            }
        """)
        drop_layout = QVBoxLayout()
        drop_layout.setContentsMargins(0, 0, 0, 0)
        drop_container.setLayout(drop_layout)
        
        # Drop area
        self.drop_area = DropArea(self)
        self.drop_area.setMinimumHeight(350)
        drop_layout.addWidget(self.drop_area)
        
        # Status label (hidden by default)
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            font-size: 14px;
            color: #4A90E2;
            padding: 10px;
            margin-top: 10px;
        """)
        self.status_label.hide()
        drop_layout.addWidget(self.status_label)
        
        main_layout.addWidget(drop_container)
        
        # Generate button (hidden until file is uploaded)
        self.generate_btn = QPushButton("Generate Worksheet")
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #4A90E2;
                border: none;
                border-radius: 25px;
                padding: 15px 40px;
                font-size: 16px;
                font-weight: 600;
                margin-top: 20px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
            QPushButton:pressed {
                background-color: #e0e0e0;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.generate_btn.setCursor(Qt.PointingHandCursor)
        self.generate_btn.clicked.connect(self.generate_worksheet)
        self.generate_btn.hide()
        main_layout.addWidget(self.generate_btn, alignment=Qt.AlignCenter)
        
    def browse_file(self):
        """Open file dialog to browse for PDF."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Course Notes PDF",
            "",
            "PDF Files (*.pdf)"
        )
        
        if file_path:
            self.process_file(file_path)
    
    def process_file(self, file_path):
        """Process the uploaded PDF file."""
        try:
            self.input_pdf_path = file_path
            
            # Extract questions
            summaries = self.pdf_generator.extract_questions_from_pdf(file_path)
            
            # Get file name
            file_name = os.path.basename(file_path)
            
            # Show success status
            if self.pdf_generator.sections:
                num_sections = len(self.pdf_generator.sections)
                section_list = "\n".join(f"  • {s}" for s in summaries)
                self.status_label.setText(
                    f"✓ {file_name}\n"
                    f"Found {num_sections} section(s):\n{section_list}"
                )
                self.status_label.setStyleSheet("""
                    font-size: 13px;
                    color: #28a745;
                    padding: 10px;
                    margin-top: 10px;
                """)
                self.status_label.show()
                self.generate_btn.show()
            else:
                self.status_label.setText(
                    f"✗ No pages with 'Section X.Y Problems' found in {file_name}"
                )
                self.status_label.setStyleSheet("""
                    font-size: 14px;
                    color: #dc3545;
                    padding: 10px;
                    margin-top: 10px;
                """)
                self.status_label.show()
                self.generate_btn.hide()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error processing PDF:\n{str(e)}")
    
    def generate_worksheet(self):
        """Generate the worksheet PDF."""
        if not self.input_pdf_path:
            QMessageBox.warning(self, "No File", "Please upload a PDF file first.")
            return
        
        # Ask where to save
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Worksheet As",
            "worksheet.pdf",
            "PDF Files (*.pdf)"
        )
        
        if not output_path:
            return
        
        try:
            # Disable button during generation
            self.generate_btn.setEnabled(False)
            self.status_label.setText("⏳ Generating worksheet...")
            self.status_label.setStyleSheet("""
                font-size: 14px;
                color: #4A90E2;
                padding: 10px;
                margin-top: 10px;
            """)
            
            # Generate PDF
            self.pdf_generator.generate_worksheet_pdf(output_path)
            
            # Success
            QMessageBox.information(
                self,
                "Success",
                f"Worksheet generated successfully!\n\nSaved to:\n{output_path}"
            )
            
            # Reset
            self.status_label.setText("✓ Worksheet generated successfully!")
            self.status_label.setStyleSheet("""
                font-size: 14px;
                color: #28a745;
                padding: 10px;
                margin-top: 10px;
            """)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generating worksheet:\n{str(e)}")
            self.status_label.setText("✗ Error generating worksheet")
            self.status_label.setStyleSheet("""
                font-size: 14px;
                color: #dc3545;
                padding: 10px;
                margin-top: 10px;
            """)
        finally:
            self.generate_btn.setEnabled(True)
