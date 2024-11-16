import sys
import os
import json
import base64
import requests
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                           QComboBox, QListWidget, QMessageBox, QDialog,
                           QSpinBox, QProgressBar, QStackedWidget)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon, QFont

class ConfigManager:
    def __init__(self):
        self.config_file = os.path.expanduser('~/.tvhrec.conf')
        self.servers = self.load_servers()

    def load_servers(self):
        if not os.path.exists(self.config_file):
            return {}
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except:
            return {}

    def save_servers(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.servers, f)

    def add_server(self, name, url, username, password):
        encoded_pass = base64.b64encode(password.encode()).decode()
        self.servers[name] = {
            'url': url,
            'username': username,
            'password': encoded_pass
        }
        self.save_servers()

    def get_server(self, name):
        if name in self.servers:
            server = self.servers[name]
            return {
                'url': server['url'],
                'username': server['username'],
                'password': base64.b64decode(server['password'].encode()).decode()
            }
        return None

class AddServerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Server")
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Server Name
        name_layout = QHBoxLayout()
        name_label = QLabel("Server Name:")
        self.name_input = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # Server URL
        url_layout = QHBoxLayout()
        url_label = QLabel("Server URL:")
        self.url_input = QLineEdit()
        self.url_input.setText("http://127.0.0.1:9981")
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)

        # Username
        username_layout = QHBoxLayout()
        username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)

        # Password
        password_layout = QHBoxLayout()
        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)

        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def get_values(self):
        return {
            'name': self.name_input.text(),
            'url': self.url_input.text().rstrip('/'),  # Remove trailing slash if present
            'username': self.username_input.text(),
            'password': self.password_input.text()
        }

class RecordingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Recording Settings")
        self.setMinimumWidth(300)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Duration
        duration_layout = QHBoxLayout()
        duration_label = QLabel("Duration (minutes):")
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 480)  # 1 minute to 8 hours
        self.duration_spin.setValue(30)
        duration_layout.addWidget(duration_label)
        duration_layout.addWidget(self.duration_spin)
        layout.addLayout(duration_layout)

        # Buttons
        button_layout = QHBoxLayout()
        start_button = QPushButton("Start Recording")
        start_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(start_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def get_duration(self):
        return self.duration_spin.value()

class TVHeadendRecorder(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.current_server = None
        self.channels = {}
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("TVHeadend Recorder")
        self.setMinimumSize(800, 600)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Server selection
        server_layout = QHBoxLayout()
        server_label = QLabel("Server:")
        self.server_combo = QComboBox()
        self.server_combo.currentTextChanged.connect(self.server_selected)
        server_layout.addWidget(server_label)
        server_layout.addWidget(self.server_combo)
        
        # Add Server button
        add_server_btn = QPushButton("Add Server")
        add_server_btn.clicked.connect(self.add_server)
        server_layout.addWidget(add_server_btn)
        
        main_layout.addLayout(server_layout)

        # Channel list
        channel_label = QLabel("Available Channels:")
        main_layout.addWidget(channel_label)
        
        self.channel_list = QListWidget()
        self.channel_list.itemSelectionChanged.connect(self.channel_selected)
        main_layout.addWidget(self.channel_list)

        # Recording controls
        control_layout = QHBoxLayout()
        self.record_btn = QPushButton("Record Selected Channel")
        self.record_btn.clicked.connect(self.start_recording)
        self.record_btn.setEnabled(False)
        control_layout.addWidget(self.record_btn)
        main_layout.addLayout(control_layout)

        # Status bar for messages
        self.statusBar().showMessage("Ready")

        # Load saved servers
        self.load_servers()

    def load_servers(self):
        self.server_combo.clear()
        for server_name in self.config_manager.servers.keys():
            self.server_combo.addItem(server_name)

    def add_server(self):
        dialog = AddServerDialog(self)
        if dialog.exec():
            values = dialog.get_values()
            if self.test_connection(values['url'], values['username'], values['password']):
                self.config_manager.add_server(
                    values['name'], values['url'], 
                    values['username'], values['password']
                )
                self.load_servers()
                self.server_combo.setCurrentText(values['name'])
            else:
                QMessageBox.warning(self, "Connection Error", 
                                  "Could not connect to server. Please check your settings.")

    def test_connection(self, url, username, password):
        try:
            response = requests.get(
                f"{url}/api/serverinfo",
                auth=(username, password) if username and password else None,
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Connection test error: {str(e)}")
            return False

    def server_selected(self, server_name):
        if not server_name:
            return
        
        self.current_server = self.config_manager.get_server(server_name)
        if self.current_server:
            self.fetch_channels()

    def channel_selected(self):
        self.record_btn.setEnabled(bool(self.channel_list.selectedItems()))

    def fetch_channels(self):
        try:
            response = requests.get(
                f"{self.current_server['url']}/api/channel/grid",
                auth=(self.current_server['username'], self.current_server['password'])
                if self.current_server['username'] and self.current_server['password']
                else None,
                timeout=5
            )
            
            if response.status_code == 200:
                self.channel_list.clear()
                self.channels = {}
                
                for channel in response.json()['entries']:
                    self.channel_list.addItem(channel['name'])
                    self.channels[channel['name']] = channel['uuid']
                
                self.statusBar().showMessage("Channels loaded successfully")
            else:
                self.statusBar().showMessage(f"Failed to load channels: {response.status_code}")
        except Exception as e:
            self.statusBar().showMessage(f"Error loading channels: {str(e)}")

    def start_recording(self):
        selected_items = self.channel_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Error", "Please select a channel to record")
            return

        channel_name = selected_items[0].text()
        channel_uuid = self.channels[channel_name]

        dialog = RecordingDialog(self)
        if dialog.exec():
            duration = dialog.get_duration()
            self.create_recording(channel_uuid, duration)

    def create_recording(self, channel_uuid, duration):
        try:
            start_time = int(datetime.now().timestamp())
            stop_time = start_time + (duration * 60)

            # Format the data as expected by TVHeadend API
            data = f"conf={{\"start\":{start_time},\"stop\":{stop_time},\"channel\":\"{channel_uuid}\",\"title\":{{\"eng\":\"Instant Recording\"}},\"subtitle\":{{\"eng\":\"Recorded via GUI\"}}}}"

            response = requests.post(
                f"{self.current_server['url']}/api/dvr/entry/create",
                auth=(self.current_server['username'], self.current_server['password'])
                if self.current_server['username'] and self.current_server['password']
                else None,
                data=data,  # Send as form data, not JSON
                headers={'Content-Type': 'application/x-www-form-urlencoded'},  # Add proper content type
                timeout=5
            )

            # Debug information
            self.statusBar().showMessage(f"API Response: {response.status_code} - {response.text}")

            if response.status_code in [200, 201]:
                QMessageBox.information(
                    self, "Success", 
                    f"Recording scheduled for {duration} minutes"
                )
                self.statusBar().showMessage("Recording started successfully")
            else:
                QMessageBox.warning(
                    self, "Error", 
                    f"Failed to start recording. Status code: {response.status_code}, Response: {response.text}"
                )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", 
                f"Error starting recording: {str(e)}"
            )

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = TVHeadendRecorder()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
