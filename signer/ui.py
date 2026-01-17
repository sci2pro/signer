import shlex
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, \
    QWidget, QFormLayout

from ops import label_certificates, parse_args


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Signer")
        self.setFixedSize(800, 600)

        layout = QFormLayout()
        # names file: label | lineedit | filedialog
        names_layout = QHBoxLayout()
        self.names_file = QLineEdit()
        self.names_file.setPlaceholderText("Select names file...")
        self.names_file.setReadOnly(True)
        names_layout.addWidget(self.names_file)
        self.names_browse_button = QPushButton("Browse...")
        self.names_browse_button.clicked.connect(self.select_names_file)
        names_layout.addWidget(self.names_browse_button)
        layout.addRow(QLabel("Names file"), names_layout)

        # template file: label | lineedit | filedialog
        template_layout = QHBoxLayout()
        self.template_file = QLineEdit()
        template_layout.addWidget(self.template_file)
        self.template_browse_button = QPushButton("Browse...")
        self.template_browse_button.clicked.connect(self.select_template_file)
        template_layout.addWidget(self.template_browse_button)
        layout.addRow(QLabel("Template file"), template_layout)

        # font file: label | linedit | filedialog
        fonts_layout = QHBoxLayout()
        self.fonts_file = QLineEdit()
        fonts_layout.addWidget(self.fonts_file)
        self.fonts_browse_button = QPushButton("Browse...")
        self.fonts_browse_button.clicked.connect(self.select_font_file)
        fonts_layout.addWidget(self.fonts_browse_button)
        layout.addRow(QLabel("Font file"), fonts_layout)

        # actions
        self.label_button = QPushButton("Label")
        self.label_button.clicked.connect(self.label)
        self.close_button = QPushButton("Exit")
        self.close_button.clicked.connect(self.close)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.label_button)
        button_layout.addWidget(self.close_button)
        button_layout.setAlignment(Qt.AlignRight)

        # layout = QVBoxLayout()
        # layout.addLayout(names_layout)
        # layout.addLayout(template_layout)
        # layout.addLayout(fonts_layout)
        layout.addRow(button_layout)

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

    def select_names_file(self):
        file_name, selectedFilter = QFileDialog.getOpenFileName(self, "Open file", "./", "*.csv *.txt *.tsv")
        self.names_file.setText(file_name)

    def select_template_file(self):
        file_name, selectedFilter = QFileDialog.getOpenFileName(self, "Open file", "./",
                                                                "*.png *.jpg *.jpeg *.tiff *.tif")
        self.template_file.setText(file_name)

    def select_font_file(self):
        file_name, selectedFilter = QFileDialog.getOpenFileName(self, "Open file", "./", "*.off *.otf *.ttf")
        self.fonts_file.setText(file_name)

    def label(self):
        print(f"Labeling...")
        sys.argv = shlex.split(
            f"signer label -n '{self.names_file.text()}' -t '{self.template_file.text()}' -F '{self.fonts_file.text()}'")
        args = parse_args()
        label_certificates(args)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
