import customtkinter as ctk
import cv2
import threading
from PIL import Image, ImageTk
import yt_dlp

def get_youtube_stream_url(youtube_url):
    ydl_opts = {
        'quiet': True,
        'format': 'best[ext=mp4]/best',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(youtube_url, download=False)
        return info_dict['url']

def ChooseCapDevice():
    class CapDeviceChooser:
        def __init__(self):
            self.cap = None
            self.preview_thread = None
            self.running = False
            self.selected_source = None

            # Main Window
            self.window = ctk.CTk()
            self.window.title("Choose Capture Device")
            self.window.geometry("800x600")

            # Left frame for controls
            self.control_frame = ctk.CTkFrame(self.window, width=200)
            self.control_frame.pack(side="left", fill="y", padx=10, pady=10)

            # Right frame for preview
            self.preview_frame = ctk.CTkFrame(self.window, width=600, height=600)
            self.preview_frame.pack(side="right", expand=True, fill="both", padx=10, pady=10)

            # Canvas for preview
            self.preview_canvas = ctk.CTkCanvas(self.preview_frame, width=600, height=600, bg="black")
            self.preview_canvas.pack(expand=True, fill="both")

            # Video source selection
            self.source_var = ctk.StringVar(value="Select a source")
            self.source_dropdown = ctk.CTkComboBox(
                self.control_frame,
                variable=self.source_var,
                values=["Capture card", "Video file", "Youtube link", "Video link"],
                command=self.update_ui,
                state="readonly"
            )
            self.source_dropdown.pack(pady=10)

            # Webcam dropdown
            self.webcam_var = ctk.StringVar(value="Select a webcam")
            self.webcam_dropdown = ctk.CTkComboBox(
                self.control_frame, 
                variable=self.webcam_var, 
                values=[], 
                state="readonly"
            )
            self.webcam_dropdown.pack(pady=10)
            self.webcam_dropdown.pack_forget()

            # Textbox for URLs or file paths
            self.textbox = ctk.CTkEntry(self.control_frame, placeholder_text="Enter file path or URL")
            self.textbox.pack(pady=10)
            self.textbox.pack_forget()

            # Preview button
            self.preview_button = ctk.CTkButton(self.control_frame, text="Preview", command=self.start_preview)
            self.preview_button.pack(pady=10)

            # Stop Preview button
            self.stop_preview_button = ctk.CTkButton(self.control_frame, text="Stop Preview", command=self.stop_preview)
            self.stop_preview_button.pack(pady=10)

            # Select button
            self.select_button = ctk.CTkButton(self.control_frame, text="Select", command=self.select_cap)
            self.select_button.pack(pady=10)

            # Initialize webcam options
            self.update_webcam_list()

        def update_ui(self, selected_option):
            self.webcam_dropdown.pack_forget()
            self.textbox.pack_forget()

            if selected_option == "Capture card":
                self.webcam_dropdown.pack()
            else:
                self.textbox.pack()

        def update_webcam_list(self):
            webcams = []
            for i in range(10):  # Check first 5 indices for connected webcams
                cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
                if cap.isOpened():
                    # Use device names if available, else fallback to index
                    device_name = f"Webcam {i}"  # Fallback name
                    if hasattr(cv2, 'VideoCaptureAPIs') and hasattr(cv2.VideoCaptureAPIs, 'CAP_DSHOW'):
                        device_name = f"Device {i}"
                    webcams.append(f"{device_name} ({i})")
                    cap.release()
            self.webcam_dropdown.configure(values=webcams if webcams else ["No webcams found"])

        def start_preview(self):
            self.stop_preview()

            selected_option = self.source_var.get()
            if selected_option == "Capture card":
                if "(" in self.webcam_var.get():
                    index = int(self.webcam_var.get().split('(')[-1][:-1])
                    self.cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
                    self.selected_source = index
            elif selected_option in ["Video file", "Video link"]:
                source = self.textbox.get()
                self.cap = cv2.VideoCapture(source)
                self.selected_source = source
            elif selected_option == "Youtube link":
                stream_url = get_youtube_stream_url(self.textbox.get())
                self.cap = cv2.VideoCapture(stream_url)
                self.selected_source = stream_url

            if self.cap and self.cap.isOpened():
                self.running = True
                self.preview_thread = threading.Thread(target=self.show_preview)
                self.preview_thread.start()

        def stop_preview(self):
            self.running = False
            if self.cap and self.cap.isOpened():
                self.cap.release()
                self.cap = None

        def show_preview(self):
            while self.running and self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret:
                    break

                # Resize frame to fit preview window
                frame = cv2.resize(frame, (600, 600), interpolation=cv2.INTER_AREA)

                # Convert frame to RGB and display in the canvas
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(frame)
                image_tk = ImageTk.PhotoImage(image=image)

                self.preview_canvas.create_image(0, 0, anchor="nw", image=image_tk)
                self.preview_canvas.image = image_tk

            self.running = False
            if self.cap:
                self.cap.release()

        def select_cap(self):
            self.stop_preview()
            self.window.quit()
            self.window.destroy()

        def run(self):
            self.window.mainloop()
            # Reinitialize cap to ensure it's usable after the window closes
            if isinstance(self.selected_source, int):
                return cv2.VideoCapture(self.selected_source, cv2.CAP_DSHOW)
            elif isinstance(self.selected_source, str):
                return cv2.VideoCapture(self.selected_source)
            return None

    app = CapDeviceChooser()
    cap = app.run()
    return cap




if __name__ == "__main__":
    cap = ChooseCapDevice()
