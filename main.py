import os
import glob
from tkinter import Tk, Frame, Label, Button, Text, Scale, Entry, IntVar, HORIZONTAL, END, LEFT, RIGHT, X
from tkinter import filedialog, ttk
from tkinter import messagebox
import PIL.Image
import threading

window = Tk()
window.geometry("1200x600")  # Example: width=800, height=600

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

    # List all main and subdirectories
    folder_list = []
    for root, dirs, _ in os.walk(selected_dir):
        for d in dirs:
            folder_list.append(os.path.join(root, d))
    # Always include the selected_dir itself
    all_folders = [selected_dir] + folder_list
    text_widget.insert(END, "Folders selected:\n")
    for folder in all_folders:
        text_widget.insert(END, folder + "\n")
    text_widget.insert(END, "\n")

    # Display all .jpg and .png images in the text widget (including subdirectories)
    files = glob.glob(selected_dir + "/**/*.jpg", recursive=True) + glob.glob(selected_dir + "/**/*.png", recursive=True)
    for file in files:
        filenames.append(os.path.basename(file))
        text_widget.insert(END, os.path.basename(file) + "\n")


def convertImages():
    global selected_dir, filenames
    if selected_dir:
        # Clear the text_widget at the start of conversion
        window.after(0, lambda: text_widget.delete(1.0, END))
        # Walk through all directories and subdirectories
        all_image_files = []
        for root, dirs, files in os.walk(selected_dir):
            # Find all jpg/png images in this directory
            images = [f for f in files if f.lower().endswith(('.jpg', '.png'))]
            if images:
                # Create 'webp' and 'thumb' folders in this directory
                webp_dir = os.path.join(root, 'webp')
                thumb_dir = os.path.join(root, 'thumb')
                os.makedirs(webp_dir, exist_ok=True)
                os.makedirs(thumb_dir, exist_ok=True)
                # Add full paths for conversion
                for img in images:
                    all_image_files.append((root, img, webp_dir, thumb_dir))

        if not all_image_files:
            window.after(0, lambda: messagebox.showinfo("No Images Found", "No Images found"))
            return

        progress["maximum"] = len(all_image_files)

        for i, (img_dir, img_name, webp_dir, thumb_dir) in enumerate(all_image_files):
            file = os.path.join(img_dir, img_name)
            try:
                img = PIL.Image.open(file)
                # Save WEBP in the local webp folder
                webp_path = os.path.join(webp_dir, os.path.splitext(img_name)[0] + ".webp")
                img.save(webp_path, "WEBP", quality=quality.get())

                # Generate thumbnail
                thumb = img.copy()
                w_percent = (thumbnail_size.get() / float(thumb.size[0]))
                h_size = int((float(thumb.size[1]) * float(w_percent)))
                thumb = thumb.resize((thumbnail_size.get(), h_size), PIL.Image.LANCZOS)
                thumb_name = os.path.splitext(img_name)[0] + "_THUMB.webp"
                thumb_path = os.path.join(thumb_dir, thumb_name)
                thumb.save(thumb_path, "WEBP", quality=quality.get())
            except Exception as e:
                print(f"Error converting {file}: {e}")

            # Show file name and first subdirectory in text_widget
            rel_path = os.path.relpath(img_dir, selected_dir)
            first_subdir = rel_path.split(os.sep)[0] if os.sep in rel_path else rel_path
            display_name = img_name
            if first_subdir and first_subdir != '.':
                display_name = f"{first_subdir}/{img_name}"
            window.after(0, lambda name=display_name: text_widget.insert(END, name + "\n"))

            # Update file status and progress bar in a thread-safe way
            window.after(0, update_file_status, img_name, "...DONE")
            window.after(0, update_progress, i + 1)


def update_progress(value):
    progress["value"] = value


def start_conversion():
    # Create a separate thread for the conversion process
    threading.Thread(target=convertImages).start()


def browseDirectories_threaded():
    threading.Thread(target=browseDirectories).start()


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
button_explore = Button(content_frame, text="Browse Folders", command=browseDirectories_threaded)
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
