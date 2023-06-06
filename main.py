import os
import glob
from tkinter import *
from tkinter import filedialog, ttk
import PIL.Image
import threading

# Store the directory
selected_dir = None

# Store the filenames
filenames = []

def update_file_status(file, status):
    # Update the status of a file in the text_widget
    index = filenames.index(file)
    text_widget.delete(f"{index + 1}.0", f"{index + 1}.end")
    text_widget.insert(f"{index + 1}.0", file + status)

def browseDirectories():
    global selected_dir, filenames
    selected_dir = filedialog.askdirectory(initialdir="/",
                                           title="Select a Directory")
    # Change label contents
    label_file_explorer.configure(text="Directory Opened: " + selected_dir)

    # Clear the text widget and filenames list
    text_widget.delete(1.0, END)
    filenames.clear()

    # Display all .jpg and .png images in the text widget
    for file in glob.glob(selected_dir + "/*.jpg") + glob.glob(selected_dir + "/*.png"):
        filenames.append(os.path.basename(file))
        text_widget.insert(END, os.path.basename(file) + '\n')

def convertImages():
    global selected_dir, filenames
    if selected_dir:
        files = glob.glob(selected_dir + "/*.jpg") + glob.glob(selected_dir + "/*.png")

        # Set the maximum value for the progress bar
        progress['maximum'] = len(files)

        # Create WEBP directory inside the selected directory
        webp_dir = os.path.join(selected_dir, "WEBP")
        os.makedirs(webp_dir, exist_ok=True)

        for i, file in enumerate(files):
            img = PIL.Image.open(file)
            webp_path = os.path.splitext(file)[0] + "_WEBP.webp"
            webp_path = os.path.join(webp_dir, os.path.basename(webp_path))
            img.save(webp_path, "WEBP")

            # Update file status and progress bar in a thread-safe way
            window.after(0, update_file_status, os.path.basename(file), "...DONE")
            window.after(0, update_progress, i+1)




def update_progress(value):
    progress['value'] = value

def start_conversion():
    # Create a separate thread for the conversion process
    threading.Thread(target=convertImages).start()

window = Tk()

# Set window title
window.title('JPG/PNG to WEBP Converter GUI')

# Create two frames, one for the content and one for the buttons and progress bar
content_frame = Frame(window)
button_frame = Frame(window)

# Pack frames, bottom frame sticks to the south ('s')
content_frame.pack(side='top', fill='both', expand=True)
button_frame.pack(side='bottom', fill='x')

# Add your widgets to the content_frame
label_file_explorer = Label(content_frame, text="***Folder Path will be here***", width=100, height=4, fg="blue")
button_explore = Button(content_frame, text="Browse Folders", command=browseDirectories)
text_widget = Text(content_frame, width=40, height=10)

label_file_explorer.pack(fill='x')
button_explore.pack(fill='x')
text_widget.pack(fill='both', expand=True)

# Add your buttons and progress bar to the button_frame
progress = ttk.Progressbar(button_frame, length=100, mode='determinate')
button_convert = Button(button_frame, text="Convert Images", command=start_conversion, height=2)
button_exit = Button(button_frame, text="Exit", command=exit, height=2)

progress.pack(fill='x')
button_convert.pack(side=LEFT, fill=X, expand=1)
button_exit.pack(side=RIGHT, fill=X, expand=1)

# Let the window wait for any events
window.mainloop()
