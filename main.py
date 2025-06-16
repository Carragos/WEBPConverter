import os
import glob
from tkinter import Tk, Frame, Label, Button, Text, Scale, Entry, IntVar, HORIZONTAL, END, LEFT, RIGHT, X
from tkinter import filedialog, ttk
import PIL.Image
import threading

window = Tk()

# Store the directory
selected_dir = None

# Store the filenames
filenames = []

# Global variable for quality
quality = IntVar()
quality.set(90)  # Set initial quality level

# Global variable for thumbnail size (width)
thumbnail_size = IntVar()
thumbnail_size.set(150)  # Default thumbnail width


def update_file_status(file, status):
    # Update the status of a file in the text_widget
    index = filenames.index(file)
    text_widget.delete(f"{index + 1}.0", f"{index + 1}.end")
    text_widget.insert(f"{index + 1}.0", file + status)


def browseDirectories():
    global selected_dir, filenames
    selected_dir = filedialog.askdirectory(initialdir="/", title="Select a Directory")
    # Change label contents
    label_file_explorer.configure(text="Directory Opened: " + selected_dir)

    # Clear the text widget and filenames list
    text_widget.delete(1.0, END)
    filenames.clear()

    # Display all .jpg and .png images in the text widget
    for file in glob.glob(selected_dir + "/*.jpg") + glob.glob(selected_dir + "/*.png"):
        filenames.append(os.path.basename(file))
        text_widget.insert(END, os.path.basename(file) + "\n")


def convertImages():
    global selected_dir, filenames
    if selected_dir:
        files = glob.glob(selected_dir + "/*.jpg") + glob.glob(selected_dir + "/*.png")

        # Set the maximum value for the progress bar
        progress["maximum"] = len(files)

        # Create WEBP directory inside the selected directory
        webp_dir = os.path.join(selected_dir, "WEBP")
        os.makedirs(webp_dir, exist_ok=True)

        # Create THUMBNAILS directory inside the selected directory
        thumbnails_dir = os.path.join(selected_dir, "THUMBNAILS")
        os.makedirs(thumbnails_dir, exist_ok=True)

        for i, file in enumerate(files):
            try:
                img = PIL.Image.open(file)
                webp_path = os.path.splitext(file)[0] + "_WEBP.webp"
                webp_path = os.path.join(webp_dir, os.path.basename(webp_path))
                img.save(webp_path, "WEBP", quality=quality.get())

                # Generate thumbnail
                thumb = img.copy()
                # Calculate new height to maintain aspect ratio
                w_percent = (thumbnail_size.get() / float(thumb.size[0]))
                h_size = int((float(thumb.size[1]) * float(w_percent)))
                thumb = thumb.resize((thumbnail_size.get(), h_size), PIL.Image.LANCZOS)
                thumb_name = os.path.splitext(os.path.basename(file))[0] + "_THUMB.webp"
                thumb_path = os.path.join(thumbnails_dir, thumb_name)
                thumb.save(thumb_path, "WEBP", quality=quality.get())
            except Exception as e:
                print(f"Error converting {file}: {e}")

            # Update file status and progress bar in a thread-safe way
            window.after(0, update_file_status, os.path.basename(file), "...DONE")
            window.after(0, update_progress, i + 1)


def update_progress(value):
    progress["value"] = value


def start_conversion():
    # Create a separate thread for the conversion process
    threading.Thread(target=convertImages).start()


# Set window title
window.title("JPG/PNG to WEBP Converter GUI")

# Create three frames: content, controls (for sliders), and button (for actions)
content_frame = Frame(window)
controls_frame = Frame(window)
button_frame = Frame(window)

content_frame.pack(side="top", fill="both", expand=True)
controls_frame.pack(side="top", fill="x", padx=10, pady=(5, 0))
button_frame.pack(side="bottom", fill="x")

# Add your widgets to the content_frame
label_file_explorer = Label(
    content_frame, text="***Folder Path will be here***", width=100, height=4, fg="blue"
)
button_explore = Button(content_frame, text="Browse Folders", command=browseDirectories)
text_widget = Text(content_frame, width=40, height=10)

label_file_explorer.pack(fill="x")
button_explore.pack(fill="x")
text_widget.pack(fill="both", expand=True)

# --- Controls Frame: Quality and Thumbnail sliders ---
quality_label = Label(controls_frame, text="Quality:")
slider = Scale(
    controls_frame,
    from_=50,
    to=100,
    orient=HORIZONTAL,
    variable=quality,
    tickinterval=10,
    length=200,
)
quality_display = Entry(controls_frame, textvariable=quality, width=3)

thumb_label = Label(controls_frame, text="Thumbnail Width:")
thumb_slider = Scale(
    controls_frame,
    from_=100,
    to=600,
    orient=HORIZONTAL,
    variable=thumbnail_size,
    tickinterval=100,
    length=200,
)
thumb_entry = Entry(controls_frame, textvariable=thumbnail_size, width=4)

# Arrange controls in a grid for clarity
quality_label.grid(row=0, column=0, padx=(0, 5), pady=2)
slider.grid(row=0, column=1, padx=(0, 10), pady=2)
quality_display.grid(row=0, column=2, padx=(0, 15), pady=2)

thumb_label.grid(row=0, column=3, padx=(0, 5), pady=2)
thumb_slider.grid(row=0, column=4, padx=(0, 10), pady=2)
thumb_entry.grid(row=0, column=5, pady=2)

# --- Button Frame: Convert and Exit buttons ---
progress = ttk.Progressbar(button_frame, length=100, mode="determinate")
button_convert = Button(
    button_frame, text="Convert Images", command=start_conversion, height=2
)
button_exit = Button(button_frame, text="Exit", command=exit, height=2)

progress.pack(fill="x")
button_exit.pack(side=LEFT, fill=X, expand=1)
button_convert.pack(side=RIGHT, fill=X, expand=1)


# Let the window wait for any events
window.mainloop()
