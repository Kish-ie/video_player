import tkinter as tk
from tkinter import filedialog, messagebox
import vlc
import time


class MediaPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("MPA - Media Player")
        self.root.geometry("1200x800")  # Default window size
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)  # Handling window close event

        # VLC player instance
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        # Video display
        self.video_frame = tk.Frame(root, bg="black")
        self.video_frame.pack(expand=True, fill="both", side=tk.LEFT)  # Occupies most space
        self.video_widget = tk.Canvas(self.video_frame, bg="black")
        self.video_widget.pack(expand=True, fill="both")

        # Transparent control bar
        self.control_bar = tk.Frame(self.video_frame, bg="#000080")  # Semi-transparent black
        self.control_bar.place(relx=0, rely=1, relwidth=1, anchor="sw", height=80)

        # Media queue frame
        self.queue_frame = tk.Frame(root, bg="gray", width=250)
        self.queue_frame.pack(side=tk.RIGHT, fill="y")

        self.queue_listbox = tk.Listbox(self.queue_frame, bg="white", fg="black", selectmode=tk.SINGLE)
        self.queue_listbox.pack(expand=True, fill="both", padx=5, pady=5)

        # Queue control buttons
        add_button = tk.Button(self.queue_frame, text="Add Media", command=self.add_to_queue)
        add_button.pack(fill="x", padx=5, pady=2)

        remove_button = tk.Button(self.queue_frame, text="Remove Media", command=self.remove_from_queue)
        remove_button.pack(fill="x", padx=5, pady=2)

        play_next_button = tk.Button(self.queue_frame, text="Play Next", command=self.play_next_in_queue)
        play_next_button.pack(fill="x", padx=5, pady=2)

        # Control buttons in the transparent bar
        self.play_button = tk.Button(self.control_bar, text="Play", command=self.play_media)
        self.play_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.pause_button = tk.Button(self.control_bar, text="Pause", command=self.pause_media)
        self.pause_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.stop_button = tk.Button(self.control_bar, text="Stop", command=self.stop_media)
        self.stop_button.pack(side=tk.LEFT, padx=10, pady=5)

        self.fullscreen_button = tk.Button(self.control_bar, text="Fullscreen", command=self.toggle_fullscreen)
        self.fullscreen_button.pack(side=tk.LEFT, padx=10, pady=5)

        # Seek bar
        self.seek_var = tk.DoubleVar()
        self.seek_bar = tk.Scale(
            self.control_bar,
            from_=0,
            to=100,
            orient="horizontal",
            variable=self.seek_var,
            command=self.seek_media,
            showvalue=0,
            sliderlength=10,
            bg="#333333",  # Matches the semi-transparent design
            fg="white",
        )
        self.seek_bar.pack(side=tk.LEFT, fill="x", expand=True, padx=5, pady=5)

        # Time label
        self.time_label = tk.Label(self.control_bar, text="00:00 / 00:00", bg="#000080", fg="white")
        self.time_label.pack(side=tk.RIGHT, padx=10, pady=5)

        # Volume control
        self.volume_scale = tk.Scale(
            self.control_bar,
            from_=0,
            to=200,
            orient="vertical",
            label="Volume",
            command=self.set_volume,
            sliderlength=10,
            bg="#333333",
            fg="white",
        )
        self.volume_scale.set(100)
        self.volume_scale.pack(side=tk.RIGHT, padx=5, pady=5)

        # Floating exit fullscreen button
        self.exit_fullscreen_button = tk.Button(
            self.video_frame,
            text="Exit Fullscreen",
            bg="red",
            fg="white",
            command=self.toggle_fullscreen,
        )

        # Initialize media player widget after mainloop starts
        self.root.after(100, self.bind_player)

        # Bind events
        self.video_widget.bind("<Double-Button-1>", self.toggle_fullscreen)

        # Track media playback
        self.media_queue = []
        self.is_fullscreen = False
        self.update_ui()

    def bind_player(self):
        """Bind VLC player to the Tkinter video widget."""
        self.player.set_hwnd(self.video_widget.winfo_id())

    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode."""
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)
        if self.is_fullscreen:
            self.control_bar.place_forget()
            self.queue_frame.pack_forget()
            self.exit_fullscreen_button.place(relx=1, rely=0, anchor="ne", width=120, height=30)
        else:
            self.control_bar.place(relx=0, rely=1, relwidth=1, anchor="sw", height=80)
            self.queue_frame.pack(side=tk.RIGHT, fill="y")
            self.exit_fullscreen_button.place_forget()
        self.bind_player()  # Rebind the VLC player to the video widget

    def add_to_queue(self):
        """Add media files to the queue."""
        file_paths = filedialog.askopenfilenames(
            filetypes=[("Media Files", "*.mp4;*.avi;*.mkv;*.mp3;*.wav;*.flac;*.ts")]
        )
        for file_path in file_paths:
            self.media_queue.append(file_path)
            self.queue_listbox.insert(tk.END, file_path.split("/")[-1])

    def remove_from_queue(self):
        """Remove the selected media file from the queue."""
        selected = self.queue_listbox.curselection()
        if selected:
            index = selected[0]
            self.media_queue.pop(index)
            self.queue_listbox.delete(index)
        else:
            messagebox.showwarning("No Selection", "Please select a media file to remove.")

    def play_next_in_queue(self):
        """Play the next media file in the queue."""
        if self.media_queue:
            next_file = self.media_queue.pop(0)
            self.queue_listbox.delete(0)
            self.play_media_file(next_file)
        else:
            messagebox.showwarning("Queue Empty", "No media files in the queue.")

    def play_media_file(self, file_path):
        """Play a specific media file."""
        media = self.instance.media_new(file_path)
        self.player.set_media(media)
        self.player.play()

    def play_media(self):
        """Play the current media."""
        if not self.player.get_media() and self.media_queue:
            self.play_next_in_queue()
        elif self.player.get_media():
            self.player.play()
        else:
            messagebox.showwarning("No Media", "Please open a media file first.")

    def pause_media(self):
        """Pause the media if playing."""
        if self.player.is_playing():
            self.player.pause()

    def stop_media(self):
        """Stop the media playback."""
        self.player.stop()

    def set_volume(self, volume_level):
        """Set the player's volume."""
        self.player.audio_set_volume(int(volume_level))

    def seek_media(self, value):
        """Seek to the specified position in the media."""
        if self.player.get_media():
            duration = self.player.get_length() / 1000
            seek_time = (float(value) / 100) * duration
            self.player.set_time(int(seek_time * 1000))

    def update_ui(self):
        """Update UI elements like the seek bar and time label."""
        if self.player.get_media():
            # Update seek bar
            duration = self.player.get_length() / 1000  # Convert ms to seconds
            if duration > 0:
                current_time = self.player.get_time() / 1000  # Convert ms to seconds
                position = (current_time / duration) * 100
                self.seek_var.set(position)

                # Update time label
                formatted_time = self.format_time(current_time)
                formatted_duration = self.format_time(duration)
                self.time_label.config(text=f"{formatted_time} / {formatted_duration}")

        self.root.after(500, self.update_ui)

    @staticmethod
    def format_time(seconds):
        """Format seconds into HH:MM:SS."""
        return time.strftime("%H:%M:%S", time.gmtime(seconds))

    def on_close(self):
        """Handle the window close event gracefully."""
        self.player.stop()
        self.root.quit()
        self.root.destroy()


# Create the Tkinter application
root = tk.Tk()
player = MediaPlayer(root)
root.mainloop()
