import sys
import json
from datetime import datetime, timedelta
import requests
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QLabel, QLineEdit, QPushButton,
                            QComboBox, QMessageBox, QGroupBox, QListWidget)
from PyQt6.QtCore import Qt

class TVHeadendRecorder(QMainWindow):
    def __init__(self):
        super().__init__()
        self.channels = {}  # Store channel UUID mapping
        self.initUI()

    def initUI(self):
        self.setWindowTitle('TVHeadend Recorder')
        self.setMinimumWidth(500)

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Server Configuration Group
        server_group = QGroupBox("Server Configuration")
        server_layout = QVBoxLayout()

        # Server URL
        url_layout = QHBoxLayout()
        url_label = QLabel("Server URL:")
        self.url_input = QLineEdit("http://127.0.0.1:9981")
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        server_layout.addLayout(url_layout)

        # Username
        user_layout = QHBoxLayout()
        user_label = QLabel("Username:")
        self.user_input = QLineEdit()
        user_layout.addWidget(user_label)
        user_layout.addWidget(self.user_input)
        server_layout.addLayout(user_layout)

        # Password
        pass_layout = QHBoxLayout()
        pass_label = QLabel("Password:")
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        pass_layout.addWidget(pass_label)
        pass_layout.addWidget(self.pass_input)
        server_layout.addLayout(pass_layout)

        # Connect button
        self.connect_btn = QPushButton("Connect to Server")
        self.connect_btn.clicked.connect(self.connect_to_server)
        server_layout.addWidget(self.connect_btn)

        server_group.setLayout(server_layout)
        layout.addWidget(server_group)

        # Channel Selection Group
        channel_group = QGroupBox("Channel Selection")
        channel_layout = QVBoxLayout()

        # Channel list
        self.channel_list = QListWidget()
        channel_layout.addWidget(self.channel_list)

        channel_group.setLayout(channel_layout)
        layout.addWidget(channel_group)

        # Recording Configuration Group
        recording_group = QGroupBox("Recording Configuration")
        recording_layout = QVBoxLayout()

        # Duration selection
        duration_layout = QHBoxLayout()
        duration_label = QLabel("Duration:")
        self.duration_combo = QComboBox()
        self.duration_combo.addItems([
            "30 minutes",
            "1 hour",
            "2 hours",
            "3 hours",
            "4 hours"
        ])
        duration_layout.addWidget(duration_label)
        duration_layout.addWidget(self.duration_combo)
        recording_layout.addLayout(duration_layout)

        # Record button
        self.record_btn = QPushButton("Start Recording")
        self.record_btn.clicked.connect(self.start_recording)
        self.record_btn.setEnabled(False)
        recording_layout.addWidget(self.record_btn)

        recording_group.setLayout(recording_layout)
        layout.addWidget(recording_group)

    def connect_to_server(self):
        try:
            auth = None
            if self.user_input.text() or self.pass_input.text():
                auth = (self.user_input.text(), self.pass_input.text())

            # Test connection
            response = requests.get(f"{self.url_input.text()}/api/serverinfo", auth=auth)
            if response.status_code == 200:
                self.fetch_channels(auth)
                QMessageBox.information(self, "Success", "Connected to server successfully!")
                self.record_btn.setEnabled(True)
            else:
                QMessageBox.warning(self, "Error", "Failed to connect to server")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection error: {str(e)}")

    def fetch_channels(self, auth):
        try:
            response = requests.get(f"{self.url_input.text()}/api/channel/grid", auth=auth)
            data = response.json()
            
            self.channel_list.clear()
            self.channels.clear()
            
            for entry in data['entries']:
                self.channel_list.addItem(entry['name'])
                self.channels[entry['name']] = entry['uuid']
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch channels: {str(e)}")

    def start_recording(self):
        if not self.channel_list.currentItem():
            QMessageBox.warning(self, "Warning", "Please select a channel to record")
            return

        channel_name = self.channel_list.currentItem().text()
        channel_uuid = self.channels[channel_name]
        
        # Get duration in seconds
        duration_text = self.duration_combo.currentText()
        if "minutes" in duration_text:
            duration = int(duration_text.split()[0]) * 60
        else:
            duration = int(duration_text.split()[0]) * 3600

        start_time = int(datetime.now().timestamp())
        stop_time = start_time + duration

        auth = None
        if self.user_input.text() or self.pass_input.text():
            auth = (self.user_input.text(), self.pass_input.text())

        try:
            conf = {
                "start": start_time,
                "stop": stop_time,
                "channel": channel_uuid,
                "title": {"eng": "Instant Recording"},
                "subtitle": {"eng": "Recorded via GUI"}
            }

            response = requests.post(
                f"{self.url_input.text()}/api/dvr/entry/create",
                data={"conf": json.dumps(conf)},
                auth=auth
            )

            if response.status_code == 200:
                QMessageBox.information(
                    self,
                    "Success",
                    f"Recording started for {channel_name}\nDuration: {self.duration_combo.currentText()}"
                )
            else:
                QMessageBox.warning(self, "Error", "Failed to start recording")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Recording error: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = TVHeadendRecorder()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
