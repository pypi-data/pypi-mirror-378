import random
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont
from PySide6.QtCore import Qt

class CaptchaCore:
    def __init__(self, type=1, length=5, width=200, height=80):
        self.type = type
        self.length = length
        self.width = width
        self.height = height
        self.text = ""
        self.pixmap = None

    def generate_text(self):
        if self.type == 1:
            self.text = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=self.length))
        elif self.type == 2:
            self.text = "".join(random.choices("0123456789", k=self.length))
        elif self.type == 3:
            self.text = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ0123456789", k=self.length))
        return self.text

    def generate_image(self):
        if not self.text:
            self.generate_text()
        pixmap = QPixmap(self.width, self.height)
        pixmap.fill(Qt.black)
        painter = QPainter(pixmap)
        for i, char in enumerate(self.text):
            angle = random.randint(-30,30) if self.type==1 else random.randint(-10,10)
            color = QColor(random.randint(100,255), random.randint(100,255), random.randint(100,255)) if self.type==1 else QColor(255,255,255)
            painter.setPen(color)
            painter.setFont(QFont("Arial", 28, QFont.Bold))
            painter.save()
            painter.translate(35*i+20, 40)
            painter.rotate(angle)
            painter.drawText(-15,15,char)
            painter.restore()
        lines = 15 if self.type==1 else (5 if self.type==3 else 2)
        for _ in range(lines):
            color = QColor(random.randint(50,200), random.randint(50,200), random.randint(50,200))
            painter.setPen(color)
            x1, y1 = random.randint(0,self.width), random.randint(0,self.height)
            x2, y2 = random.randint(0,self.width), random.randint(0,self.height)
            painter.drawLine(x1,y1,x2,y2)
        painter.end()
        self.pixmap = pixmap
        return pixmap
