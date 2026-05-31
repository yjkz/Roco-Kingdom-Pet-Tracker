import os
import sys
from PySide6.QtGui import QImage, QPainter, QColor, QPen, QBrush, QGuiApplication
from PySide6.QtCore import Qt, QRect

def create_image(filename, width, height, draw_func):
    img = QImage(width, height, QImage.Format_ARGB32)
    img.fill(Qt.transparent)
    painter = QPainter(img)
    painter.setRenderHint(QPainter.Antialiasing)
    draw_func(painter, width, height)
    painter.end()
    img.save(filename)

def draw_bg_main(p, w, h):
    p.setPen(QPen(QColor("#E5C07B"), 10))
    p.setBrush(QBrush(QColor("#FDF5E6")))
    p.drawRoundedRect(5, 5, w-10, h-10, 20, 20)
    
    p.setPen(Qt.NoPen)
    p.setBrush(QBrush(QColor("#4682B4")))
    p.drawRoundedRect(10, 10, w-20, 50, 15, 15)
    p.drawRect(10, 30, w-20, 30)

def draw_btn_normal(p, w, h):
    p.setPen(QPen(QColor("#DAA520"), 4))
    p.setBrush(QBrush(QColor("#5F9EA0")))
    p.drawRoundedRect(2, 2, w-4, h-4, 10, 10)

def draw_btn_pressed(p, w, h):
    p.setPen(QPen(QColor("#B8860B"), 4))
    p.setBrush(QBrush(QColor("#4F8284")))
    p.drawRoundedRect(2, 2, w-4, h-4, 10, 10)

def draw_avatar_frame(p, w, h):
    p.setPen(QPen(QColor("#DAA520"), 8))
    p.setBrush(Qt.NoBrush)
    p.drawRoundedRect(4, 4, w-8, h-8, 15, 15)

def draw_slider_groove(p, w, h):
    p.setPen(QPen(QColor("#A9A9A9"), 2))
    p.setBrush(QBrush(QColor("#E0E0E0")))
    p.drawRoundedRect(1, 1, w-2, h-2, h//2 - 1, h//2 - 1)

def draw_slider_handle(p, w, h):
    p.setPen(QPen(QColor("#DAA520"), 2))
    p.setBrush(QBrush(QColor("#87CEFA")))
    p.drawEllipse(1, 1, w-2, h-2)

def draw_icon_settings(p, w, h):
    p.setPen(QPen(Qt.white, 3))
    p.setBrush(Qt.NoBrush)
    p.drawEllipse(w//4, h//4, w//2, h//2)
    p.drawText(QRect(0,0,w,h), Qt.AlignCenter, "S")

def draw_icon_close(p, w, h):
    p.setPen(QPen(Qt.white, 3))
    p.setBrush(Qt.NoBrush)
    p.drawText(QRect(0,0,w,h), Qt.AlignCenter, "X")

if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    ui_dir = os.path.join("E:\\ClaudeGame\\RockKingdom\\xuan fu chuang-plugin", "assets", "ui")
    os.makedirs(ui_dir, exist_ok=True)
    
    create_image(os.path.join(ui_dir, "bg_main.png"), 200, 200, draw_bg_main)
    create_image(os.path.join(ui_dir, "btn_bg_normal.png"), 60, 40, draw_btn_normal)
    create_image(os.path.join(ui_dir, "btn_bg_pressed.png"), 60, 40, draw_btn_pressed)
    create_image(os.path.join(ui_dir, "avatar_frame.png"), 100, 100, draw_avatar_frame)
    create_image(os.path.join(ui_dir, "slider_groove.png"), 100, 10, draw_slider_groove)
    create_image(os.path.join(ui_dir, "slider_handle.png"), 20, 20, draw_slider_handle)
    create_image(os.path.join(ui_dir, "btn_icon_settings.png"), 30, 30, draw_icon_settings)
    create_image(os.path.join(ui_dir, "btn_icon_close.png"), 30, 30, draw_icon_close)
    
    print(f"Placeholder images generated in {ui_dir}")
