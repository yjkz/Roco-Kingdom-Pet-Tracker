from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPainter, QPainterPath, QPen, QBrush, QColor, QFontMetrics
from PySide6.QtCore import Qt

class StrokedLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._stroke_color = QColor("#5C4033") # Dark brown
        self._stroke_width = 3
        self._fill_color = QColor("#FFF8DC")   # Light cream/yellow
        
    def setStrokeColor(self, color):
        self._stroke_color = QColor(color)
        self.update()
        
    def setStrokeWidth(self, width):
        self._stroke_width = width
        self.update()
        
    def setFillColor(self, color):
        self._fill_color = QColor(color)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        text = self.text()
        if not text:
            return
            
        path = QPainterPath()
        font = self.font()
        fm = QFontMetrics(font)
        
        # Calculate alignment
        rect = self.rect()
        flags = int(self.alignment())
        
        # QPainterPath.addText requires the baseline point
        # A simple approximation for centering:
        text_rect = fm.boundingRect(rect, flags, text)
        
        x = rect.x()
        y = rect.y()
        
        if flags & Qt.AlignHCenter:
            x = rect.x() + (rect.width() - text_rect.width()) / 2
        elif flags & Qt.AlignRight:
            x = rect.width() - text_rect.width()
            
        if flags & Qt.AlignVCenter:
            y = rect.y() + (rect.height() + fm.ascent() - fm.descent()) / 2
        elif flags & Qt.AlignBottom:
            y = rect.height() - fm.descent()
        else:
            y = rect.y() + fm.ascent() # AlignTop
            
        path.addText(x, y, font, text)
        
        # Draw stroke
        pen = QPen(self._stroke_color, self._stroke_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)
        
        # Draw fill
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(self._fill_color))
        painter.drawPath(path)
        
        painter.end()
