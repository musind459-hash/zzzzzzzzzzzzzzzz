import sys
import os
import random
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, 
                             QSlider, QComboBox, QPushButton, QSpinBox, 
                             QHBoxLayout, QFileDialog, QSystemTrayIcon, QMenu)
from PyQt6.QtCore import Qt, QTimer, QPoint, QSize
from PyQt6.QtGui import QPixmap, QIcon, QAction

# Название файла твоей иконки (замени, если расширение другое)
ICON_FILE = "icon.png" 

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class SpritePet(QWidget):
    def __init__(self, image_path, speed, scale_percent, opacity_value, screen_limit):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowOpacity(opacity_value / 100)
        
        self.label = QLabel(self)
        original_pixmap = QPixmap(image_path)
        
        if original_pixmap.isNull():
            original_pixmap = QPixmap(50, 50)
            original_pixmap.fill(Qt.GlobalColor.magenta)

        new_width = max(5, int(original_pixmap.width() * (scale_percent / 100)))
        new_height = max(5, int(original_pixmap.height() * (scale_percent / 100)))
        
        self.pixmap = original_pixmap.scaled(new_width, new_height, 
                                            Qt.AspectRatioMode.KeepAspectRatio, 
                                            Qt.TransformationMode.SmoothTransformation)
        self.label.setPixmap(self.pixmap)
        self.resize(self.pixmap.size())

        self.speed = speed
        self.screen_limit = screen_limit
        self.move(random.randint(0, max(0, self.screen_limit.width() - self.width())), 
                  random.randint(0, max(0, self.screen_limit.height() - self.height())))
        
        self.direction = QPoint(random.choice([-1, 1]), random.choice([-1, 1]))
        self.timer = QTimer()
        self.timer.timeout.connect(self.move_sprite)
        self.timer.start(20)

    def move_sprite(self):
        new_pos = self.pos() + self.direction * self.speed
        if new_pos.x() <= 0 or new_pos.x() + self.width() >= self.screen_limit.width():
            self.direction.setX(self.direction.x() * -1)
        if new_pos.y() <= 0 or new_pos.y() + self.height() >= self.screen_limit.height():
            self.direction.setY(self.direction.y() * -1)
        self.move(new_pos)

class ControlMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ZEROKS Gif")
        self.setFixedSize(400, 720)
        
        # Установка основной иконки окна
        self.main_icon_path = resource_path(ICON_FILE)
        if os.path.exists(self.main_icon_path):
            self.setWindowIcon(QIcon(self.main_icon_path))

        self.setStyleSheet("""
            QWidget { background-color: #050505; color: #00ffff; font-family: 'Consolas', sans-serif; }
            QLabel { font-size: 10px; text-transform: uppercase; margin-top: 8px; color: #0088ff; }
            QSlider::groove:horizontal { border: 1px solid #00ffff; height: 2px; background: #111; }
            QSlider::handle:horizontal { background: #00ffff; width: 12px; margin: -5px 0; border-radius: 6px; }
            QPushButton { border: 1px solid #00ffff; padding: 8px; background: #000; margin-top: 10px; font-weight: bold; }
            QPushButton:hover { background: #00ffff; color: #000; }
            QSpinBox, QComboBox { background: #111; border: 1px solid #00ffff; padding: 4px; color: #00ffff; }
        """)
        
        layout = QVBoxLayout()
        
        # Настройка разрешения
        layout.addWidget(QLabel("РАЗРЕШЕНИЕ ЭКРАНА:"))
        res_layout = QHBoxLayout()
        self.res_w = QSpinBox(); self.res_w.setRange(100, 8000)
        self.res_h = QSpinBox(); self.res_h.setRange(100, 5000)
        screen = QApplication.primaryScreen().geometry()
        self.res_w.setValue(screen.width()); self.res_h.setValue(screen.height())
        res_layout.addWidget(self.res_w); res_layout.addWidget(self.res_h)
        layout.addLayout(res_layout)

        # Выбор спрайта
        layout.addWidget(QLabel("ВЫБОР СПРАЙТА:"))
        self.sprite_selector = QComboBox()
        self.sprite_paths = {
            "sprite1": resource_path("sprite1.png"),
            "sprite2": resource_path("sprite2.png"),
            "sprite3": resource_path("sprite3.png")
        }
        self.sprite_selector.addItems(self.sprite_paths.keys())
        layout.addWidget(self.sprite_selector)

        self.btn_add_custom = QPushButton("+ ДОБАВИТЬ СВОЙ PNG")
        self.btn_add_custom.clicked.connect(self.add_custom_sprite)
        layout.addWidget(self.btn_add_custom)

        # Слайдеры
        self.lbl_size = QLabel("Размер: 100%"); layout.addWidget(self.lbl_size)
        self.scale_slider = QSlider(Qt.Orientation.Horizontal); self.scale_slider.setRange(1, 500)
        self.scale_slider.setValue(100); self.scale_slider.valueChanged.connect(lambda v: self.lbl_size.setText(f"Размер: {v}%"))
        layout.addWidget(self.scale_slider)

        self.lbl_speed = QLabel("Скорость: 5"); layout.addWidget(self.lbl_speed)
        self.speed_slider = QSlider(Qt.Orientation.Horizontal); self.speed_slider.setRange(1, 100)
        self.speed_slider.setValue(5); self.speed_slider.valueChanged.connect(lambda v: self.lbl_speed.setText(f"Скорость: {v}"))
        layout.addWidget(self.speed_slider)

        self.lbl_opacity = QLabel("Прозрачность: 100%"); layout.addWidget(self.lbl_opacity)
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal); self.opacity_slider.setRange(5, 100)
        self.opacity_slider.setValue(100); self.opacity_slider.valueChanged.connect(lambda v: self.lbl_opacity.setText(f"Прозрачность: {v}%"))
        layout.addWidget(self.opacity_slider)

        layout.addWidget(QLabel("КОЛИЧЕСТВО:"))
        self.count_spin = QSpinBox(); self.count_spin.setRange(1, 100); layout.addWidget(self.count_spin)

        self.btn_spawn = QPushButton("ЗАПУСТИТЬ")
        self.btn_spawn.clicked.connect(self.spawn_pets); layout.addWidget(self.btn_spawn)

        self.btn_clear = QPushButton("УДАЛИТЬ ВСЕХ")
        self.btn_clear.clicked.connect(self.clear_pets); layout.addWidget(self.btn_clear)

        self.setLayout(layout)
        self.active_pets = []

        # НАСТРОЙКА ТРЕЯ
        self.setup_tray()

    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        if os.path.exists(self.main_icon_path):
            self.tray_icon.setIcon(QIcon(self.main_icon_path))
        else:
            # Если иконки нет, ставим дефолтную точку
            self.tray_icon.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon))
        
        self.tray_icon.setToolTip("ZEROKS Sprite Engine")
        
        tray_menu = QMenu()
        show_action = QAction("Открыть настройки", self)
        show_action.triggered.connect(self.showNormal)
        exit_action = QAction("Полный выход", self)
        exit_action.triggered.connect(QApplication.instance().quit)
        
        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_click)
        self.tray_icon.show()

    def on_tray_click(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible(): self.hide()
            else: self.showNormal()

    def closeEvent(self, event):
        if self.tray_icon.isVisible():
            self.hide()
            event.ignore()

    def add_custom_sprite(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите PNG", "", "Images (*.png *.jpg *.webp)")
        if file_path:
            name = os.path.basename(file_path)
            self.sprite_paths[name] = file_path
            self.sprite_selector.addItem(name)
            self.sprite_selector.setCurrentText(name)

    def spawn_pets(self):
        name = self.sprite_selector.currentText()
        path = self.sprite_paths.get(name)
        selected_res = QSize(self.res_w.value(), self.res_h.value())
        if path and os.path.exists(path):
            for _ in range(self.count_spin.value()):
                pet = SpritePet(path, self.speed_slider.value(), self.scale_slider.value(), self.opacity_slider.value(), selected_res)
                pet.show()
                self.active_pets.append(pet)

    def clear_pets(self):
        for pet in self.active_pets: pet.close()
        self.active_pets.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    menu = ControlMenu()
    menu.show()
    sys.exit(app.exec())