import tkinter as tk
from tkinter import filedialog, messagebox
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from gdrive import UploadToGdrive
# Initialize GoogleAuth
gauth = GoogleAuth()

# Load client secrets
gauth.LoadClientConfigFile("client_secrets.json")


def enter_text():
    # Get text from entry widget and insert it into the text display widget
    input_text = entry.get()
    if input_text.strip():
        text_display.insert(tk.END, input_text + '\n')
        entry.delete(0, tk.END)
    else:
        messagebox.showwarning("Input Error", "Text entry field is empty!")

def upload_file():
    # Open file dialog to select a file
    file_path = filedialog.askopenfilename(
        title="Select a file",
        filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
    )
    if file_path:
     #   raw_file = r'{}'.format(file_path)
        message=UploadToGdrive(gauth,file_path)
        text_display.insert(tk.END, file_path + '\n')
        text_display.insert(tk.END, "uploaded file" + '\n')
        entry.delete(0, tk.END)

# Create the main window
root = tk.Tk()
root.title("Text Entry and File Upload GUI")

# Create a Text widget for displaying text
text_display = tk.Text(root, height=20, width=80)
text_display.pack(padx=10, pady=10)

# Create a frame to hold the entry and buttons
entry_frame = tk.Frame(root)
entry_frame.pack(padx=10, pady=5)

# Create an Entry widget for text input
entry = tk.Entry(entry_frame, width=50)
entry.pack(side=tk.LEFT, padx=(0, 5))

# Create an Enter button to process text input
enter_button = tk.Button(entry_frame, text="Enter", command=enter_text)
enter_button.pack(side=tk.LEFT, padx=(0, 5))

# Create an Upload File button to upload a file
upload_button = tk.Button(entry_frame, text="Upload File", command=upload_file)
upload_button.pack(side=tk.LEFT)

# Run the main event loop
root.mainloop()
