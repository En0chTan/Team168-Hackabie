import sys
import struct
import wave
import pyaudio
import pvporcupine
import pvcobra
import pyttsx3
import webbrowser
from openai import OpenAI
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QGraphicsView, QGraphicsScene, QGraphicsObject,
    QStackedWidget, QPushButton, QTextEdit, QScrollArea
)
from PyQt5.QtCore import (
    QThread, pyqtSignal, Qt, QRectF, QPropertyAnimation, pyqtProperty, QEasingCurve
)
from PyQt5.QtGui import QPainter, QBrush, QColor, QFont
from dotenv import dotenv_values


class AnimatedEllipse(QGraphicsObject):
    def __init__(self, rect, color):
        super().__init__()

        #yy
        self.tts = pyttsx3.init()
        #yy

        self._rect = rect
        self._color = color

    def boundingRect(self):
        return QRectF(0, 0, 200, 200)

    def paint(self, painter, option, widget):
        painter.setBrush(QBrush(self._color))
        painter.setRenderHint(QPainter.Antialiasing)
        painter.drawEllipse(self._rect)

    def getRect(self):
        return self._rect

    def setRect(self, rect):
        self.prepareGeometryChange()
        self._rect = rect
        self.update()

    rect = pyqtProperty(QRectF, fget=getRect, fset=setRect)


class BreathingSphere(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setFixedSize(240, 240)
        self.setStyleSheet("background: transparent; border: none;")
        self.setAlignment(Qt.AlignCenter)

        self.dark_ellipse = AnimatedEllipse(QRectF(50, 50, 100, 100), QColor("#1e1b7e"))
        self.light_ellipse = AnimatedEllipse(QRectF(50, 50, 100, 100), QColor("#443fd9"))

        self.scene.addItem(self.dark_ellipse)
        self.scene.addItem(self.light_ellipse)

        self.dark_anim = QPropertyAnimation(self.dark_ellipse, b"rect")
        self.light_anim = QPropertyAnimation(self.light_ellipse, b"rect")
        for anim in (self.dark_anim, self.light_anim):
            anim.setDuration(1000)
            anim.setLoopCount(-1)
            anim.setEasingCurve(QEasingCurve.InOutQuad)

    def start_breathing(self):
        self.dark_anim.setStartValue(QRectF(50, 50, 100, 100))
        self.dark_anim.setEndValue(QRectF(40, 40, 120, 120))
        self.light_anim.setStartValue(QRectF(50, 50, 100, 100))
        self.light_anim.setEndValue(QRectF(35, 35, 130, 130))
        self.dark_anim.start()
        self.light_anim.start()

    def stop_breathing(self):
        self.dark_anim.stop()
        self.light_anim.stop()
        self.dark_ellipse.setRect(QRectF(50, 50, 100, 100))
        self.light_ellipse.setRect(QRectF(50, 50, 100, 100))


class ChatPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #2d2dff; color: white;")
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(10)

        self.title = QLabel("Message sent:")
        self.title.setFont(QFont("Arial", 18))
        self.title.setAlignment(Qt.AlignCenter)

        self.bubble_container = QVBoxLayout()
        self.bubble_container.setAlignment(Qt.AlignTop)

        self.bubble_widget = QWidget()
        self.bubble_widget.setLayout(self.bubble_container)
        self.bubble_widget.setStyleSheet("background-color: transparent;")

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.bubble_widget)
        self.scroll.setStyleSheet("background-color: transparent; border: none;")

        self.back_button = QPushButton("Back")
        self.back_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.back_button.clicked.connect(self.return_to_main)

        self.layout.addWidget(self.title)
        self.layout.addWidget(self.scroll)
        self.layout.addWidget(self.back_button, alignment=Qt.AlignCenter)
        self.setLayout(self.layout)

    def display_message(self, message):
        bubble = QLabel(message)
        bubble.setStyleSheet("""
            QLabel {
                background-color: #5c6bc0;
                border-radius: 15px;
                padding: 10px 15px;
                font-size: 16px;
                color: white;
                max-width: 220px;
            }
        """)
        bubble.setWordWrap(True)
        self.bubble_container.addWidget(bubble, alignment=Qt.AlignLeft)

    def set_main_ui(self, main_ui, stack):
        self.main_ui = main_ui
        self.stack = stack

    def return_to_main(self):
        self.stack.setCurrentWidget(self.main_ui)


class CallingPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #2d2dff; color: white;")
        layout = QVBoxLayout()
        label = QLabel("Calling in progress...")
        label.setFont(QFont("Arial", 24))
        label.setAlignment(Qt.AlignCenter)

        button = QPushButton("End Call")
        button.setStyleSheet("font-size: 18px; padding: 12px;")
        button.clicked.connect(self.return_to_main)

        layout.addStretch()
        layout.addWidget(label)
        layout.addStretch()
        layout.addWidget(button, alignment=Qt.AlignCenter)
        self.setLayout(layout)

    def set_main_ui(self, main_ui, stack):
        self.main_ui = main_ui
        self.stack = stack

    def return_to_main(self):
        self.stack.setCurrentWidget(self.main_ui)


class VoiceAssistantWorker(QThread):
    update_status = pyqtSignal(str)
    update_animation = pyqtSignal(str)
    display_transcript = pyqtSignal(str)
    trigger_call_page = pyqtSignal()
    trigger_chat_page = pyqtSignal(str)

    def __init__(self, access_key, keyword_path, filename):
        super().__init__()
        self.access_key = access_key
        self.keyword_path = keyword_path
        self.filename = filename
        self.client = OpenAI(api_key=config["OPEN-API"])
        self.tts = pyttsx3.init()

    def run(self):
        porcupine = pvporcupine.create(access_key=self.access_key, keyword_paths=[self.keyword_path])
        cobra = pvcobra.create(access_key=self.access_key)
        pa = pyaudio.PyAudio()
        audio_stream = pa.open(rate=porcupine.sample_rate, channels=1, format=pyaudio.paInt16,
        input=True, frames_per_buffer=porcupine.frame_length)

        while True:
            self.update_status.emit("Grab Assistant is ready")
            self.update_animation.emit("idle")
            record = False
            frames = []
            count = 30
            result = -1

            while True:
                pcm_b = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
                pcm = struct.unpack_from("h" * porcupine.frame_length, pcm_b)
                if result < 0:
                    result = porcupine.process(pcm)
                if result >= 0:
                    record = True
                    self.update_status.emit("Wake word detected! Recording...")

                if record:
                    self.update_animation.emit("active")
                    voice_prob = cobra.process(pcm)
                    if voice_prob < 0.3:
                        count -= 1
                        if count <= 0:
                            wf = wave.open(self.filename, 'wb')
                            wf.setnchannels(1)
                            wf.setsampwidth(pa.get_sample_size(pyaudio.paInt16))
                            wf.setframerate(porcupine.sample_rate)
                            wf.writeframes(b''.join(frames))
                            wf.close()
                            self.update_status.emit("Transcribing...")
                            self.transcribe()
                            break
                    else:
                        count = 30
                    frames.append(pcm_b)

    def transcribe(self):
        
        self.status_label = QLabel() #yy

        with open(self.filename, "rb") as audio_file:
            transcript = self.client.audio.translations.create(
                model="whisper-1",
                file=audio_file,
                prompt="Transcribe without translation."
            )

        text = transcript.text.lower()
        self.display_transcript.emit(text)
        self.update_status.emit("Grab Assistant is ready")
        self.update_animation.emit("idle")

        if "say hi" in text:
            self.tts.say("Hi there!")
            self.tts.runAndWait()
        elif "weather" in text:
            webbrowser.open("https://www.google.com/search?q=weather")
        elif "map" in text or "directions" in text:
            webbrowser.open("https://www.google.com/maps")
        elif "call the customer" in text or "call customer" in text:
            self.trigger_call_page.emit()
        elif "message passenger" in text or "message customer" in text:
            if "message passenger" in text:
                message = text.split("message passenger", 1)[-1]
            else:
                message = text.split("message customer", 1)[-1]
            message = message.strip(" ,.\"")
            self.update_status.emit("Sending message...")
            self.trigger_chat_page.emit(message)
        elif "yes" in text:
            self.tts.say("Request accepted")
            self.tts.runAndWait()
            # self.status_label.setText("Request accepted")
            self.update_status.emit("Request accepted")
        elif "no" in text:
            self.tts.say("Request declined")
            self.tts.runAndWait()
            self.update_status.emit("Request declined")

    #yy
    # def handle_yes_response(self):
    #     self.tts.say("Request accepted")
    #     self.tts.runAndWait()
    #     self.update_status.emit("Request accepted")
    # def handle_no_response(self):
    #     self.tts.say("Request declined")
    #     self.tts.runAndWait()
    #     self.update_status.emit("Request declined")
    #yy



    #yy
    # def listen_for_response(self):
    #     pa = pyaudio.PyAudio()
    #     stream = pa.open(format=pyaudio.paInt16,
    #                     channels=1,
    #                     rate=16000,
    #                     input=True,
    #                     frames_per_buffer=1024)

    #     self.update_status.emit("Listening for response...")

    #     frames = []
    #     silence_threshold = 30  # number of silent frames before stopping
    #     silent_count = 0

    #     for _ in range(16000 // 1024 * 5):  # listen max 5 seconds
    #         data = stream.read(1024, exception_on_overflow=False)
    #         frames.append(data)

    #         audio_level = max(struct.unpack("<" + str(len(data) // 2) + "h", data))
    #         if abs(audio_level) < 500:
    #             silent_count += 1
    #             if silent_count > silence_threshold:
    #                 break
    #         else:
    #             silent_count = 0

    #     stream.stop_stream()
    #     stream.close()
    #     pa.terminate()

    #     filename = "response.wav"
    #     wf = wave.open(filename, 'wb')
    #     wf.setnchannels(1)
    #     wf.setsampwidth(pa.get_sample_size(pyaudio.paInt16))
    #     wf.setframerate(16000)
    #     wf.writeframes(b''.join(frames))
    #     wf.close()

    #     self.update_status.emit("Processing response...")
    #     self.process_response(filename)
    #yy

    #yy
    # def process_response(self, filename):
    #     with open(filename, "rb") as f:
    #         response = self.client.audio.translations.create(
    #             model="whisper-1",
    #             file=f,
    #             prompt="Transcribe response"
    #         )
    #     text = response.text.lower().strip()
    #     self.display_transcript.emit(f"You said: {text}")

    #     if "yes" in text:
    #         self.tts.say("Accepted the request.")
    #         self.tts.runAndWait()
    #         self.update_status.emit("Request accepted.")
    #     elif "no" in text:
    #         self.tts.say("Request declined.")
    #         self.tts.runAndWait()
    #         self.update_status.emit("Request declined.")
    #     else:
    #         self.tts.say("Sorry, I didn’t catch that.")
    #         self.tts.runAndWait()
    #         self.update_status.emit("Didn’t understand the response.")

    #yy


class AssistantUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Grab Assistant")
        self.setStyleSheet("background-color: #5b4dff; color: white;")
        self.setFixedSize(360, 640)

        #yy
        self.tts = pyttsx3.init()
        #yy

        self.stack = QStackedWidget()
        self.main_widget = QWidget()
        self.calling_page = CallingPage()
        self.chat_page = ChatPage()

        self.calling_page.set_main_ui(self.main_widget, self.stack)
        self.chat_page.set_main_ui(self.main_widget, self.stack)

        self.worker = VoiceAssistantWorker(
            access_key=config["PICO-API"]",
            keyword_path="hey_grab_ppn.ppn",
            filename="recording.wav"
        )
        self.worker.update_status.connect(self.update_status)
        self.worker.display_transcript.connect(self.update_transcript)
        self.worker.update_animation.connect(self.update_animation)
        self.worker.trigger_call_page.connect(self.show_calling_page)
        self.worker.trigger_chat_page.connect(self.show_chat_page)
        self.worker.start()

        self.status_label = QLabel("Grab Assistant is ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 24px; font-weight: bold;")

        self.transcript_label = QLabel("")
        self.transcript_label.setAlignment(Qt.AlignCenter)
        self.transcript_label.setWordWrap(True)

        self.sphere = BreathingSphere()

        # yy
        self.next_passenger_button = QPushButton("Next Passenger")
        self.next_passenger_button.setStyleSheet("font-size: 18px; padding: 10px; background-color: #443fd9; color: white; border-radius: 10px;")
        self.next_passenger_button.clicked.connect(self.handle_next_passenger)
        # yy

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 40, 30, 40)
        layout.addWidget(self.status_label)
        layout.addStretch()
        layout.addWidget(self.sphere, alignment=Qt.AlignCenter)
        layout.addStretch()
        layout.addWidget(self.transcript_label)

        # yy
        layout.addWidget(self.next_passenger_button, alignment=Qt.AlignCenter)
        # yy

        self.main_widget.setLayout(layout)

        self.stack.addWidget(self.main_widget)
        self.stack.addWidget(self.calling_page)
        self.stack.addWidget(self.chat_page)

        outer_layout = QVBoxLayout(self)
        outer_layout.addWidget(self.stack)
        self.setLayout(outer_layout)

    def update_status(self, text):
        self.status_label.setText(text)

    def update_transcript(self, text):
        self.transcript_label.setText(text)

    def update_animation(self, mode):
        if mode == "active":
            self.sphere.start_breathing()
        elif mode == "idle":
            self.sphere.stop_breathing()

    def show_calling_page(self):
        self.stack.setCurrentWidget(self.calling_page)

    def show_chat_page(self, message):
        self.chat_page.display_message(message)
        self.stack.setCurrentWidget(self.chat_page)

    #yy
    def handle_next_passenger(self):
        self.transcript_label.setText("")
        self.status_label.setText("Receiving a request...")
        self.stack.setCurrentWidget(self.main_widget)

        # Speak the passenger request
        self.tts.say("There is a passenger request. Do you want to accept the request?")
        self.tts.runAndWait()
    #yy

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = AssistantUI()
    ui.show()
    sys.exit(app.exec_())
