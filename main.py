import sys
import os
import cv2
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QVBoxLayout,
    QPushButton,
    QSlider,
    QFileDialog,
    QComboBox,
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from moviepy.editor import VideoFileClip


class VideoTrimmer(QWidget):
    def __init__(self):
        super().__init__()
        self.video_path = None
        self.cap = None
        self.fps = 0
        self.total_frames = 0
        self.current_frame = 0
        self.is_paused = False  # For controlling pause and play

        # Create UI elements
        self.video_label = QLabel(self)
        self.current_time_label = QLabel("Current Time: 00:00", self)
        self.start_time_label = QLabel("Start Time: 00:00", self)
        self.end_time_label = QLabel("End Time: 00:00", self)
        self.slider = QSlider(Qt.Horizontal, self)
        self.open_button = QPushButton("Open Video", self)
        self.trim_button = QPushButton("Trim Video", self)
        self.save_button = QPushButton("Save Another Video", self)
        self.start_slider = QSlider(Qt.Horizontal, self)
        self.end_slider = QSlider(Qt.Horizontal, self)
        self.pause_button = QPushButton("Pause", self)  # Pause button
        self.combo_box = QComboBox(self)  # Dropdown menu

        # Add items to combo box
        self.combo_box.addItem("Select Directory")
        self.combo_box.addItem("Fall")
        self.combo_box.addItem("Normal")
        self.output_file_dir = ""

        # Set up layout
        layout = QVBoxLayout()
        layout.addWidget(self.video_label)
        layout.addWidget(self.open_button)
        layout.addWidget(self.combo_box)
        layout.addWidget(QLabel("Start Time"))
        layout.addWidget(self.start_slider)
        layout.addWidget(QLabel("End Time"))
        layout.addWidget(self.end_slider)
        layout.addWidget(self.current_time_label)
        layout.addWidget(self.start_time_label)
        layout.addWidget(self.end_time_label)
        layout.addWidget(self.pause_button)
        layout.addWidget(self.trim_button)
        layout.addWidget(self.save_button)
        layout.addWidget(self.slider)
        self.setLayout(layout)

        # Connect signals to slots
        self.open_button.clicked.connect(self.open_video)
        self.save_button.clicked.connect(self.save_another_video)
        self.slider.valueChanged.connect(self.set_position)
        self.start_slider.valueChanged.connect(self.update_start_time)
        self.end_slider.valueChanged.connect(self.update_end_time)
        self.trim_button.clicked.connect(self.trim_video)
        self.pause_button.clicked.connect(self.toggle_pause)  # Connect pause button
        self.combo_box.activated.connect(self.select_directory)  # Dropdown selection

        # Timer for video playback
        self.timer = QTimer()
        self.timer.timeout.connect(self.play_video)

    def open_video(self):
        self.video_path, _ = QFileDialog.getOpenFileName(
            self, "Open Video", "", "Video Files (*.mp4 *.avi *.mov *.mkv)"
        )

        if not self.video_path:
            return

        # Open the video file
        self.cap = cv2.VideoCapture(self.video_path)
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Set slider properties
        self.slider.setMinimum(0)
        self.slider.setMaximum(self.total_frames - 1)
        self.start_slider.setMinimum(0)
        self.start_slider.setMaximum(self.total_frames - 1)
        self.end_slider.setMinimum(0)
        self.end_slider.setMaximum(self.total_frames - 1)
        self.end_slider.setValue(
            self.total_frames - 1
        )  # Set end slider to max by default

        # Start playing the video
        self.is_paused = False  # Ensure the video is in play mode
        self.timer.start(1000 // self.fps)

    def play_video(self):
        if not self.is_paused and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.current_frame += 1
                self.slider.setValue(self.current_frame)

                # Convert frame to QImage
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.video_label.setPixmap(QPixmap.fromImage(image))

                # Update current playback time label
                current_time_seconds = self.current_frame / self.fps
                self.current_time_label.setText(
                    f"Current Time: {self.format_time(current_time_seconds)}"
                )

                if self.current_frame >= self.total_frames - 1:
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    self.current_frame = 0
            else:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                self.current_frame = 0

    def set_position(self, position):
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, position)
            self.current_frame = position

    def toggle_pause(self):
        """Toggle play/pause state when the button is clicked."""
        if self.is_paused:
            self.is_paused = False
            self.pause_button.setText("Pause")
        else:
            self.is_paused = True
            self.pause_button.setText("Play")

    def select_directory(self):
        """Handle selection from the dropdown menu."""
        selected_option = self.combo_box.currentText()
        dir = os.path.dirname(self.video_path)

        # Define a base output file name (you can modify this as needed)
        file_name = os.path.basename(
            self.video_path
        )  # This will use the same name as the input file
        file_name = os.path.splitext(file_name)[0]  # Remove the extension

        if selected_option == "Fall":
            self.output_file_dir = f"{dir}/fall"
            if not os.path.exists(self.output_file_dir):
                os.makedirs(self.output_file_dir)

            # Define the full output file path with a valid file name and extension
            self.output_file_path = os.path.join(
                self.output_file_dir, f"{file_name}_fall.mp4"
            )
            print(f"Fall directory selected: {self.output_file_path}")

        elif selected_option == "Normal":
            self.output_file_dir = f"{dir}/normal"
            if not os.path.exists(self.output_file_dir):
                os.makedirs(self.output_file_dir)

            # Define the full output file path with a valid file name and extension
            self.output_file_path = os.path.join(
                self.output_file_dir, f"{file_name}_normal.mp4"
            )
            print(f"Normal directory selected: {self.output_file_path}")

    def trim_video(self):
        start_frame = self.start_slider.value()
        end_frame = self.end_slider.value()

        start_time = start_frame / self.fps
        end_time = end_frame / self.fps

        clip = VideoFileClip(self.video_path).subclip(start_time, end_time)
        # output_path = f"{self.output_file_dir}/{self.video_label.split('/')[-1]}"
        clip.write_videofile(self.output_file_path, codec="libx264")

        print(f"Video trimmed and saved as {self.output_file_dir}")

    def save_another_video(self):
        """Save another trimmed video."""
        # Open a new file save dialog

        # Example: You can trim or just save the currently selected video
        start_frame = self.start_slider.value()
        end_frame = self.end_slider.value()

        start_time = start_frame / self.fps
        end_time = end_frame / self.fps

        clip = VideoFileClip(self.video_path).subclip(start_time, end_time)
        clip.write_videofile(self.output_file_path, codec="libx264")

        print(f"Another video saved as {self.output_file_dir}")

    def update_start_time(self):
        start_time = self.start_slider.value() / self.fps
        self.start_time_label.setText(f"Start Time: {self.format_time(start_time)}")

    def update_end_time(self):
        end_time = self.end_slider.value() / self.fps
        self.end_time_label.setText(f"End Time: {self.format_time(end_time)}")

    def format_time(self, seconds):
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoTrimmer()
    window.setWindowTitle("Video Trimmer with Pause and Directory Selection")
    window.resize(700, 500)
    window.show()
    sys.exit(app.exec_())
