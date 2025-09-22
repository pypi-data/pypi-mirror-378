from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from .core import CaptchaCore
from .utils import detect_language
from .messages import MESSAGES

class CaptchaWidget(QWidget):
    def __init__(self, type=1, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CAPTCHA")
        self.captcha = CaptchaCore(type=type)
        self.success = False
        self.lang = detect_language()

        layout = QVBoxLayout()
        self.captcha_label = QLabel()
        self.captcha_label.setPixmap(self.captcha.generate_image())
        self.input_line = QLineEdit()
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.check_captcha)

        layout.addWidget(self.captcha_label)
        layout.addWidget(self.input_line)
        layout.addWidget(self.submit_button)
        self.setLayout(layout)

    def check_captcha(self):
        if self.input_line.text().upper() == self.captcha.text:
            QMessageBox.information(self, "Success", MESSAGES[self.lang]["success"])
            self.success = True
        else:
            QMessageBox.warning(self, "Fail", MESSAGES[self.lang]["fail"])
            self.success = False
        self.close()
