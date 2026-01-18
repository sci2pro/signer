import shlex
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, \
    QWidget, QFormLayout, QSizePolicy, QGroupBox

from ops import label_certificates, parse_args


class FileSelectHandle:
    def __init__(self, parent: QMainWindow, attribute_name: str, *, caption="Open file", dir="./", filter: str = "",
                 selectedFilter: str = "", options=QFileDialog.Options(),
                 fileMode: QFileDialog.FileMode = QFileDialog.FileMode.AnyFile):
        self.parent = parent
        self.attribute_name = attribute_name
        self.caption = caption
        self.dir = dir
        self.filter = filter
        self.selectedFilter = selectedFilter
        self.options = options
        self.fileMode = fileMode

    def __call__(self, *args):
        dialog = QFileDialog(self.parent)
        dialog.setFileMode(self.fileMode)
        if self.fileMode == QFileDialog.FileMode.Directory:
            file_name = dialog.getExistingDirectory(caption=self.caption, dir=self.dir)
        elif self.fileMode == QFileDialog.FileMode.AnyFile:
            file_name, selectedFilter = dialog.getOpenFileName(self.parent, self.caption, self.dir, self.filter,
                                                               self.selectedFilter, self.options)
        self.parent.__getattribute__(self.attribute_name).setText(file_name)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Signer")
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.setMinimumWidth(800)

        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(0)
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        # names file: label | lineedit | filedialog
        names_layout = QHBoxLayout()
        self.names_file = QLineEdit()
        self.names_file.setPlaceholderText("Select names file...")
        self.names_file.setReadOnly(True)
        names_layout.addWidget(self.names_file)
        self.names_browse_button = QPushButton("Browse...")
        self.names_browse_button.clicked.connect(
            FileSelectHandle(self, "names_file", filter="Text files (*.txt *.csv *.tsv)"))
        names_layout.addWidget(self.names_browse_button)
        form_layout.addRow(QLabel("Names file"), names_layout)

        # template file: label | lineedit | filedialog
        template_layout = QHBoxLayout()
        self.template_file = QLineEdit()
        self.template_file.setPlaceholderText("Select template file...")
        self.template_file.setReadOnly(True)
        template_layout.addWidget(self.template_file)
        self.template_browse_button = QPushButton("Browse...")
        self.template_browse_button.clicked.connect(
            FileSelectHandle(self, "template_file", filter="Images (*.png *.jpg *.jpeg *.tiff *.tif)"))
        template_layout.addWidget(self.template_browse_button)
        form_layout.addRow(QLabel("Template file"), template_layout)

        # font file: label | linedit | filedialog
        fonts_layout = QHBoxLayout()
        self.fonts_file = QLineEdit()
        self.fonts_file.setPlaceholderText("Select font file...")
        self.fonts_file.setReadOnly(True)
        fonts_layout.addWidget(self.fonts_file)
        self.fonts_browse_button = QPushButton("Browse...")
        # the argument to connect has to be a callable
        # I need a callable that takes arguments
        self.fonts_browse_button.clicked.connect(
            FileSelectHandle(self, "fonts_file", filter="Font files (*.otf *.off *.ttf *.woff)"))
        fonts_layout.addWidget(self.fonts_browse_button)
        form_layout.addRow(QLabel("Font file"), fonts_layout)

        # output directory: label | linedit | filedialog
        output_layout = QHBoxLayout()
        self.output_dir = QLineEdit()
        self.output_dir.setPlaceholderText("Select output directory")
        self.output_dir.setReadOnly(True)
        output_layout.addWidget(self.output_dir)
        self.output_browse_button = QPushButton("Browse...")
        self.output_browse_button.clicked.connect(
            FileSelectHandle(self, "output_dir", options=QFileDialog.Options.ShowDirsOnly,
                             fileMode=QFileDialog.FileMode.Directory))
        output_layout.addWidget(self.output_browse_button)
        form_layout.addRow(QLabel("Output directory"), output_layout)

        # font: spinbox | size | colour
        # font_group = QGroupBox("Font")
        # font_layout = QHBoxLayout()
        # font_layout.addWidget(QLabel("Name"))
        # font_layout.addWidget(QFont)
        # font_group.setLayout(font_layout)

        form_layout.addRow(QLabel("Font file"), font_layout)

        # actions
        self.label_button = QPushButton("Label")
        self.label_button.clicked.connect(self.label)
        self.close_button = QPushButton("Exit")
        self.close_button.clicked.connect(self.close)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.label_button)
        button_layout.addWidget(self.close_button)
        button_layout.setAlignment(Qt.AlignRight)

        form_layout.addRow(button_layout)

        widget = QWidget()
        widget.setLayout(form_layout)

        self.setCentralWidget(widget)

    def label(self):
        print(f"Labeling...")
        sys.argv = shlex.split(
            f"signer label -n '{self.names_file.text()}' "
            f"-t '{self.template_file.text()}' "
            f"-F '{self.fonts_file.text()}' "
            f"-O '{self.output_dir.text()}'"
        )
        args = parse_args()
        label_certificates(args)


def main():
    app = QApplication(sys.argv)
    # app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
