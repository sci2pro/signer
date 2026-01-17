import argparse
import pathlib
import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageDraw, ImageFont, ImageTk


def label_certificates(args):
    names = list()
    with open(args.names, "r") as f:
        names = f.readlines()
    if not args.output_dir.exists():
        print(f"Creating output directory '{args.output_dir}'...")
        args.output_dir.mkdir(parents=True)
    for name in names:
        # write text on the image at location
        img = Image.open(args.template)
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(args.font_path, args.font_size)
        # we need to know the length of the font so that we can adjust
        font_width = font.getlength(name)
        text_colour = hex_to_rgb(args.font_colour)  # red
        # get the location to sign
        with open("../name_coords.txt") as f:
            name_coords = f.readlines()
        text_x, text_y = tuple(map(int, name_coords[0].split(",")))
        # adjust the x value
        draw.text((text_x - font_width / 2, text_y), name, font=font, fill=text_colour)
        img.save(args.output_dir / f"{name.strip().replace(' ', '_')}-certificate.{args.output_format}")
    return


def view_template(args: argparse.Namespace):
    image_viewer = ImageViewer(args.image_name, show_grid=args.show_grid)
    image_viewer.run()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    # label parser
    label_parser = subparsers.add_parser("label", help="Label image")
    label_parser.add_argument("-n", "--names", help="A CSV file with a name on each row")
    label_parser.add_argument("-t", "--template", help="A template image")
    label_parser.add_argument("-O", "--output-dir", default="output_dir", type=pathlib.Path, help="Output directory")
    label_parser.add_argument("-f", "--output-format", default="png",
                              choices=["png", "tif", "tiff", "jpeg", "jpg", "webp", "bmp", "pdf", "eps", "gif", "jp2",
                                       "j2k", "jpx"], help="Output format [default: png]")
    label_parser.add_argument("-F", "--font-path", default="fonts/arial.ttf", help="Font file [default: arial.ttf]")
    label_parser.add_argument("-S", "--font-size", default=50, type=int, help="Font size [default: 50]")
    label_parser.add_argument("-C", "--font-colour", default="#000000",
                              help="Font colour in hex (don't forget to quote the colour e.g., '#ff22aa' [default: '#000000']")

    # view parser
    view_parser = subparsers.add_parser("view", help="Image viewer")
    view_parser.add_argument("image_name", help="Image name")
    view_parser.add_argument("-g", "--show-grid", action="store_true",
                             help="Hide the calibration grid [default: false]")

    # gui parser
    gui_parser = subparsers.add_parser("gui", help="GUI")

    args = parser.parse_args()
    return args


def hex_to_rgb(hex):
    """Convert a hex string to an RGB tuple."""
    hex = hex.lstrip('#')
    r, g, b = hex[:2], hex[2:4], hex[4:6]
    r_int = int(r, 16)
    g_int = int(g, 16)
    b_int = int(b, 16)
    return (r_int, g_int, b_int)


class ImageViewer:
    """Zoomable and scrollable image view with Tkinter Canvas"""

    def __init__(self, image_path, show_grid=True):
        self.root = tk.Tk()
        self.root.title("Image Viewer")
        self.root.config(cursor="crosshair")
        self.image_path = image_path
        self.pil_image = Image.open(image_path)
        self.scale = 1.0  # 1:1
        self.show_grid = show_grid

        # Canvas + scrollbars
        self.canvas = tk.Canvas(self.root, highlightthickness=0, bg="#888888")
        self.hbar = ttk.Scrollbar(self.root, orient="horizontal", command=self.canvas.xview)
        self.vbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.status_bar = ttk.Frame(self.root)
        self.image_size_status = ttk.Label(self.status_bar)
        self.separator = ttk.Separator(self.status_bar, orient="vertical")
        self.mouse_position_status = ttk.Label(self.status_bar)
        self.canvas.configure(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)

        # Geometry
        w, h = self.pil_image.size
        self.canvas.configure(width=min(1200, w), height=min(900, h))
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.vbar.grid(row=0, column=1, sticky="ns")
        self.hbar.grid(row=1, column=0, sticky="ew")
        self.status_bar.grid(row=2, column=0, sticky="nsew")
        self.image_size_status.grid(row=2, column=0, sticky="nw")
        self.separator.grid(row=2, column=1, sticky="nsew")
        self.mouse_position_status.grid(row=2, column=3, sticky="ne")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Render initial image
        self.tk_image = None
        self.image_id = None
        self._render()

        # Bindings
        # Scroll (vertical/horizontal)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel_windows_macos)
        self.canvas.bind("<Shift-MouseWheel>", self._on_shift_mousewheel_windows_macos)
        self.canvas.bind("<Button-4>", self._on_linux_wheel_up)  # Linux
        self.canvas.bind("<Button-5>", self._on_linux_wheel_down)  # Linux

        # Zoom with Ctrl + wheel (Windows/macOS)
        self.canvas.bind("<Control-MouseWheel>", self._on_ctrl_wheel_zoom)
        # Zoom with Ctrl + Button-4/5 (Linux)
        self.canvas.bind("<Control-Button-4>", self._on_linux_zoom_in)
        self.canvas.bind("<Control-Button-5>", self._on_linux_zoom_out)

        # Panning with middle mouse button
        self.canvas.bind("<ButtonPress-2>", self._pan_start)
        self.canvas.bind("<B2-Motion>", self._pan_move)

        # Click to print image coordinates (relative to the original image)
        self.canvas.bind("<Button-1>", self._print_image_coords)
        self.name_coordinates_file = "../name_coords.txt"

        # Mouse moves to show the coordinates in the status bar
        self.canvas.bind("<Motion>", self._display_mouse_position)

    def _render(self):
        # Re-render the scaled image and update the scrollregion
        w, h = self.pil_image.size
        self.image_size_status.config(text=f"Image size: {w}x{h}")
        sw = max(1, int(w * self.scale))
        sh = max(1, int(h * self.scale))
        resized = self.pil_image.resize((sw, sh), Image.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(resized)
        if self.image_id is None:
            self.image_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        else:
            self.canvas.itemconfig(self.image_id, image=self.tk_image)
        self.canvas.configure(scrollregion=(0, 0, sw, sh))
        if self.show_grid:
            # Add calibration grid (red) – scales with current zoom
            # Clear any previous grid lines
            self.canvas.delete("grid")

            # vertical lines at 1/4, 1/2, 3/4 of the current scaled width
            for x in (sw / 4, sw / 2, 3 * sw / 4):
                self.canvas.create_line(x, 0, x, sh, fill="#ff0000", tags=("grid",))

            # horizontal lines at 1/4, 1/2, 3/4 of the current scaled height
            for y in (sh / 4, sh / 2, 3 * sh / 4):
                self.canvas.create_line(0, y, sw, y, fill="#ff0000", tags=("grid",))

    def _on_mousewheel_windows_macos(self, event):
        # If Ctrl is pressed, zoom instead of scroll
        if event.state & 0x0004:  # Control key mask
            self._zoom(event, 1.1 if event.delta > 0 else (1 / 1.1))
        else:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_shift_mousewheel_windows_macos(self, event):
        self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_linux_wheel_up(self, event):
        self.canvas.yview_scroll(-3, "units")

    def _on_linux_wheel_down(self, event):
        self.canvas.yview_scroll(3, "units")

    def _on_ctrl_wheel_zoom(self, event):
        self._zoom(event, 1.1 if event.delta > 0 else (1 / 1.1))

    def _on_linux_zoom_in(self, event):
        self._zoom(event, 1.1)

    def _on_linux_zoom_out(self, event):
        self._zoom(event, 1 / 1.1)

    def _zoom(self, event, factor):
        # Keep scale within reasonable bounds
        new_scale = min(8.0, max(0.1, self.scale * factor))
        if abs(new_scale - self.scale) < 1e-6:
            return

        # Record canvas view center to preserve position approximately
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        rx = cx / max(1, self.pil_image.width * self.scale)
        ry = cy / max(1, self.pil_image.height * self.scale)

        self.scale = new_scale
        self._render()

        # Restore view near the same relative point
        sw = self.pil_image.width * self.scale
        sh = self.pil_image.height * self.scale
        self.canvas.xview_moveto(max(0, min(1, rx * self.pil_image.width * self.scale / sw)))
        self.canvas.yview_moveto(max(0, min(1, ry * self.pil_image.height * self.scale / sh)))

    def _pan_start(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def _pan_move(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def _display_mouse_position(self, event):
        self.mouse_position_status.configure(text=f"Mouse position: {event.x}, {event.y}")

    def _print_image_coords(self, event):
        # Convert canvas coords to image coords, then to original-image coords
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        ix = int(cx / self.scale)
        iy = int(cy / self.scale)
        print(f"Clicked coordinates (image space): x={ix}, y={iy}")
        # write the last clicked coordinates to a file e.g., name_coords.txt
        with open(self.name_coordinates_file, "w") as f:
            print(f"Writing signature coords to file {self.name_coordinates_file}")
            f.write(f"{ix},{iy}\n")

    def run(self):
        print(f"Image size: {self.pil_image.size}")
        self.root.mainloop()
