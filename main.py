import sys
import tkinter as tk

from PIL import Image, ImageDraw, ImageFont, ImageTk


class ImageViewer:
    """Zoomable and scrollable image view with Tkinter Canvas"""

    def __init__(self, image_path):
        self.root = tk.Tk()
        self.root.title("Image Viewer")
        self.image_path = image_path
        self.pil_image = Image.open(image_path)
        self.scale = 1.0  # 1:1

        # Canvas + scrollbars
        self.canvas = tk.Canvas(self.root, highlightthickness=0, bg="#888888")
        self.hbar = tk.Scrollbar(self.root, orient="horizontal", command=self.canvas.xview)
        self.vbar = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)

        # Geometry
        w, h = self.pil_image.size
        self.canvas.configure(width=min(1000, w), height=min(800, h))
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.vbar.grid(row=0, column=1, stick="ns")
        self.hbar.grid(row=1, column=0, sticky="ew")
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
        self.coordinates_file = "signature_coords.txt"

    def _render(self):
        # Re-render the scaled image and update the scrollregion
        w, h = self.pil_image.size
        sw = max(1, int(w * self.scale))
        sh = max(1, int(h * self.scale))
        resized = self.pil_image.resize((sw, sh), Image.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(resized)
        if self.image_id is None:
            self.image_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        else:
            self.canvas.itemconfig(self.image_id, image=self.tk_image)
        self.canvas.configure(scrollregion=(0, 0, sw, sh))

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

    def _print_image_coords(self, event):
        # Convert canvas coords to image coords, then to original-image coords
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        ix = int(cx / self.scale)
        iy = int(cy / self.scale)
        print(f"Clicked coordinates (image space): x={ix}, y={iy}")
        # write the last clicked coordinates to a file e.g., signature_coords.txt
        with open(self.coordinates_file, "w") as f:
            print(f"Writing signature coords to file {self.coordinates_file}")
            f.write(f"{ix},{iy}\n")

    def run(self):
        print(f"Image size: {self.pil_image.size}")
        self.root.mainloop()


def write_text_on_png(text, png, location=None):
    # write text on the image at location
    img = Image.open(png)
    draw = ImageDraw.Draw(img)
    font_path = "arial.ttf"
    font_size = 40
    font = ImageFont.truetype(font_path, font_size)
    text_colur = (255, 0, 0)  # red
    text_position = (50, 50)
    draw.text(text_position, text, font=font, fill=text_colur)
    img.save(f"{text}-certificate.png")
    return


def get_coordinates(event):
    x, y = event.x, event.y
    print(f"Clicked coordinates: x={x}, y={y}")


def get_image_point_coordinates(image_path):
    image = Image.open(image_path)
    width, height = image.size
    root = tk.Tk()
    canvas = tk.Canvas(root, width=width, height=height)
    canvas.pack()

    print(f"Image size: {image.size}")
    photo = ImageTk.PhotoImage(image)
    canvas.create_image(0, 0, anchor=tk.NW, image=photo)
    canvas.bind("<Button-1>", get_coordinates)  # binds left-click
    root.mainloop()


def main():
    # names = [
    #     "Paul K. Korir",
    # ]
    template = "template.png"
    # for name in names:
    #     write_text_on_png(name, template)
    # get_image_point_coordinates(template)
    image_viewer = ImageViewer(template)
    image_viewer.run()
    return 0


if __name__ == '__main__':
    sys.exit(main())
