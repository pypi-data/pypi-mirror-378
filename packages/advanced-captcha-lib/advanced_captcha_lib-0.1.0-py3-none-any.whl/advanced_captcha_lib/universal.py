from .ui import CaptchaWidget
from PySide6.QtWidgets import QApplication
import sys

def run_captcha(type=1):
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    captcha = CaptchaWidget(type=type)
    captcha.show()
    app.exec()

    return getattr(captcha, "success", False)
