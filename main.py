import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import subprocess
import os
import threading

class MotionExtractionApp:
    def __init__(self, root): # TKINTER WOOWOWOWOWOWOWOWOWOWOOWOWOOOOOOOOOOOOOOOOOO
        self.root = root
        self.root.title("Motion Extraction")

        self.video_path = None
        self.cap = None
        self.frames = []
        self.current_frame_index = 0
        self.offset = 5

        self.canvas_width = 640
        self.canvas_height = 360 # eh thats probably big enough for most people
        self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack()

        self.frame_slider = tk.Scale(root, from_=0, to=0, orient='horizontal', label="Frame Position")
        self.frame_slider.pack()
        self.frame_slider.bind("<Motion>", self.update_frame_from_slider)

        self.offset_slider = tk.Scale(root, from_=0, to=20, orient='horizontal', label="Frame Offset")
        self.offset_slider.set(3)
        self.offset_slider.pack()
        self.offset_slider.bind("<Motion>", self.update_frame_from_offset)

        self.load_button = tk.Button(root, text="Load Video", command=self.load_video)
        self.load_button.pack()

        self.export_button = tk.Button(root, text="Export Video", command=self.export_video)
        self.export_button.pack()

    def load_video(self):
        self.video_path = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")])
        if self.video_path:
            self.cap = cv2.VideoCapture(self.video_path)
            self.frames = []
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break
                self.frames.append(frame)
            self.cap.release()
            self.current_frame_index = 0
            self.frame_slider.config(to=len(self.frames) - 1)
            self.show_frame()

    def show_frame(self):
        if self.frames:
            frame = self.process_frame(self.current_frame_index)
            frame = self.resize_frame(frame)
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            img_tk = ImageTk.PhotoImage(image=img)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
            self.canvas.image = img_tk

    def process_frame(self, index):
        original_frame = self.frames[index]
        offset = self.offset_slider.get()

        if index + offset < len(self.frames):
            shifted_frame = self.frames[index + offset]
            inverted_frame = cv2.bitwise_not(shifted_frame)
            blended_frame = cv2.addWeighted(original_frame, 0.5, inverted_frame, 0.5, 0)
            return blended_frame
        else:
            return original_frame

    def resize_frame(self, frame): # DO NOT LET THIS BIH GET TOO BIG or it looks all zoomed in and funnhy but not good funny
        height, width, _ = frame.shape
        aspect_ratio = width / height

        if width > height:
            new_width = self.canvas_width
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = self.canvas_height
            new_width = int(new_height * aspect_ratio)

        resized_frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
        return resized_frame

    def update_frame_from_slider(self, event):
        self.current_frame_index = self.frame_slider.get()
        self.show_frame()

    def update_frame_from_offset(self, event):
        self.show_frame()

    def export_video(self):
        def run_export():
            if self.frames:
                input_filename = os.path.splitext(os.path.basename(self.video_path))[0]
                output_filename = f"{input_filename}_motion_extracted_{self.offset_slider.get()}.mp4" # stops it from overwriting files usually most of the time occasionally
                offset = self.offset_slider.get()
                frame_count = len(self.frames) - offset
                temp_output = 'temp_output.avi'
                fourcc = cv2.VideoWriter_fourcc(*'XVID') # exporting directly to h248 was having problems :(
                out = cv2.VideoWriter(temp_output, fourcc, 30, (self.frames[0].shape[1], self.frames[0].shape[0]))
                for i in range(frame_count):
                    out.write(self.process_frame(i))
                out.release()
                subprocess.run(['ffmpeg', '-loglevel', 'quiet', '-i', temp_output, '-c:v', 'libx264', '-preset', 'slow', '-crf', '23', output_filename]) # had to switch to ffmpeg subprocess because dum dum code didnt want to work origianly
                os.remove(temp_output)
                messagebox.showinfo("Export Complete", f"The video has been successfully exported as {output_filename}!")
        export_thread = threading.Thread(target=run_export) # anoda thread to stop 'not responding' in tkiknter
        export_thread.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = MotionExtractionApp(root)
    root.mainloop()
