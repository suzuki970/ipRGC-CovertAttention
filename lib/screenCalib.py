import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPainter, QPen, QColor
from PyQt6.QtCore import Qt, QPointF
import json
import os
import config

class CalibrationWindow(QWidget):
    def __init__(self, screen_index=0, color="red", save_name="test.json"):
        super().__init__()
        self.screen_index = screen_index
        self.color = QColor(color)
        self.save_name = save_name
        
        # 使用する画面を指定
        screen = app.screens()[screen_index]
        self.setGeometry(screen.geometry())
        self.showFullScreen()
        
        # ウィンドウ上の初期9点（3x3グリッド）
        g = self.geometry()
        margin_x, margin_y = 100, 100
        width = g.width() - 2 * margin_x
        height = g.height() - 2 * margin_y
        
        self.points = []
        for i in range(3):
            for j in range(3):
                x = margin_x + j * width / 2
                y = margin_y + i * height / 2
                self.points.append(QPointF(x, y))
        
        self.original_points = [QPointF(p) for p in self.points]

        if os.path.exists(self.save_name):
            print(f"Loading existing calibration file: {self.save_name}")
            self.original_points, self.points = self.load_points_from_file(self.save_name)

        self.dragging_index = None
        self.threshold = 20
    
    def paintEvent(self, event):
        painter = QPainter(self)
        pen = QPen(QColor("lime"), 3)
        painter.setPen(pen)
    
        for pt in self.points:
            painter.setBrush(self.color)
            painter.drawEllipse(pt, 6, 6)

    def load_points_from_file(self, filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)

        original_data = data.get("original", [])
        adjusted_data = data.get("adjusted", [])

        original_points = [QPointF(x, y) for x, y in original_data]
        adjusted_points = [QPointF(x, y) for x, y in adjusted_data]

        return original_points, adjusted_points

    def mousePressEvent(self, event):
        pos = event.position()
        for i, pt in enumerate(self.points):
            if (pt - pos).manhattanLength() < self.threshold:
                self.dragging_index = i
                return

    def mouseMoveEvent(self, event):
        if self.dragging_index is not None:
            self.points[self.dragging_index] = event.position()
            self.update()

    def mouseReleaseEvent(self, event):
        self.dragging_index = None

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_S:
            self.save_points()
        elif event.key() == Qt.Key.Key_Escape:
            self.close()

    def save_points(self):
        data = {
            "original": [[p.x(), p.y()] for p in self.original_points],
            "adjusted": [[p.x(), p.y()] for p in self.points]
        }

        with open(self.save_name, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        
        print(f"Saved to {self.save_name}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    screens = app.screens()
    if len(screens) < 2:
        print("2画面が必要です。接続されていません。")
        sys.exit(1)

    win1 = CalibrationWindow(screen_index=config.SCREEN_NUM_YELLOW, color="red", save_name="screen1_points.json")
    win2 = CalibrationWindow(screen_index=config.SCREEN_NUM_BLUE, color="blue", save_name="screen2_points.json")

    sys.exit(app.exec())
