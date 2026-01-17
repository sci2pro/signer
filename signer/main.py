import sys

from PySide6.QtWidgets import QApplication

from ops import label_certificates, view_template, parse_args
from ui import MainWindow


def main():
    args = parse_args()

    # signer label -n names.csv -t template.png -F font.ttf -O output_folder
    if args.command == "label":
        label_certificates(args)
    # signer view template.png [--show-grid]
    elif args.command == "view":
        view_template(args)
    elif args.command == "gui":
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        return app.exec()

    return 0


if __name__ == '__main__':
    sys.exit(main())
