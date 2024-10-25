import customtkinter as ctk
from tkinter import filedialog
import moviepy.editor as mp
import srt
import os
import textwrap

class VideoTranscriptionCompiler(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Video Transcription Layout")
        self.geometry("600x400")
        
        # Create main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # File selection labels
        self.video_path_label = ctk.CTkLabel(self.main_frame, text="No video selected")
        self.video_path_label.pack(pady=10)
        
        self.srt_path_label = ctk.CTkLabel(self.main_frame, text="No SRT file selected")
        self.srt_path_label.pack(pady=10)
        
        # Progress and status
        self.progress_bar = ctk.CTkProgressBar(self.main_frame)
        self.progress_bar.pack(pady=20, fill="x")
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(self.main_frame, text="")
        self.status_label.pack(pady=10)
        
        # Control buttons
        self.button_frame = ctk.CTkFrame(self.main_frame)
        self.button_frame.pack(pady=20)
        
        self.load_video_btn = ctk.CTkButton(
            self.button_frame,
            text="Load Video",
            command=self.load_video
        )
        self.load_video_btn.pack(side="left", padx=10)
        
        self.load_srt_btn = ctk.CTkButton(
            self.button_frame,
            text="Load SRT",
            command=self.load_srt
        )
        self.load_srt_btn.pack(side="left", padx=10)
        
        self.process_btn = ctk.CTkButton(
            self.button_frame,
            text="Process Video",
            command=self.process_video
        )
        self.process_btn.pack(side="left", padx=10)
        
        self.video_path = ""
        self.srt_path = ""

    def load_video(self):
        self.video_path = filedialog.askopenfilename(
            filetypes=[("Video files", "*.mp4 *.avi *.mkv")]
        )
        if self.video_path:
            self.video_path_label.configure(
                text=f"Video: {os.path.basename(self.video_path)}"
            )
            
    def load_srt(self):
        self.srt_path = filedialog.askopenfilename(
            filetypes=[("Subtitle files", "*.srt")]
        )
        if self.srt_path:
            self.srt_path_label.configure(
                text=f"SRT: {os.path.basename(self.srt_path)}"
            )

    def create_subtitle_clips(self):
        with open(self.srt_path, 'r', encoding='utf-8') as f:
            subs = list(srt.parse(f.read()))
        
        subtitle_clips = []
        for sub in subs:
            start_time = sub.start.total_seconds()
            end_time = sub.end.total_seconds()
            duration = end_time - start_time

            # Wrap the subtitle content to fit 75% of the width
            wrapped_content = '\n'.join(textwrap.wrap(sub.content, width=40))  # Adjust width if necessary
            
            # Create text clip with larger font and wrapped content
            text_clip = mp.TextClip(
                wrapped_content,
                fontsize=40,  # Increased font size
                font='Courier', 
                color='white',
                bg_color='black',
                size=(1080, None),  # Width matches video width
                method='caption'
            )
            
            # Position the text clip in the designated area
            text_clip = text_clip.set_position(('center', 650))  # Adjust Y position as needed
            text_clip = text_clip.set_start(start_time).set_duration(duration)
            subtitle_clips.append(text_clip)
        
        return subtitle_clips
    
    def process_video(self):
        if not self.video_path or not self.srt_path:
            self.status_label.configure(text="Please select both video and SRT files")
            return
            
        try:
            self.status_label.configure(text="Processing video...")
            self.progress_bar.set(0.1)
            
            # Load and resize video if needed
            video = mp.VideoFileClip(self.video_path)
            video = video.resize(width=1080)  # Set width to 1080p
            
            # Create subtitle clips
            subtitle_clips = self.create_subtitle_clips()
            
            # Combine all elements
            final_clip = mp.CompositeVideoClip(
                [video] + subtitle_clips,
                size=(1080, 1920)  # Full HD vertical size
            )
            
            self.progress_bar.set(0.6)
            
            # Generate output path
            output_path = os.path.splitext(self.video_path)[0] + "_with_subs.mp4"
            
            # Write final video
            final_clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                fps=24
            )
            
            self.progress_bar.set(1.0)
            self.status_label.configure(
                text=f"Video saved as: {os.path.basename(output_path)}"
            )
            
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}")
            self.progress_bar.set(0)

if __name__ == "__main__":
    app = VideoTranscriptionCompiler()
    app.mainloop()