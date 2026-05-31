import os
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QAction, QIcon, QPixmap, QPainter
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QScrollArea,
    QMenu,
    QApplication,
    QDialog,
)

from models.pokemon_data import PokemonEntry
from views.pokemon_card import PokemonCard
from views.components import StrokedLabel

_UI_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "ui")
_SETTINGS_ICON_PATHS = [
    os.path.join(_UI_DIR, "btn_icon_settings.png"),
    "E:/ClaudeGame/570+Icons-CN-v1.0.3/1.用户界面/设置_64px.png",
]


class TitleBar(QWidget):
    """Custom title bar that supports drag-to-move on the entire bar area."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._parent = parent
        self._drag_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and self._drag_pos is not None:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self._drag_pos = event.globalPosition().toPoint()
            if self._parent:
                self._parent.move(self._parent.x() + delta.x(), self._parent.y() + delta.y())


class OverlayWindow(QWidget):
    """Main frameless, always-on-top overlay window for the Pokemon counter."""

    add_pokemon_requested = Signal()
    edit_pokemon_requested = Signal(str)
    remove_pokemon_requested = Signal(str)
    settings_changed = Signal()

    def __init__(self, app_state):
        super().__init__()
        self._app_state = app_state
        self._config = app_state.config
        self._drag_pos = None
        self._cards = []
        self._bg_pixmap = QPixmap(os.path.join(_UI_DIR, "bg_main_2.png"))

        self.setWindowTitle("精灵计数器")
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.setFixedWidth(getattr(self._config, "window_width", 320))

        self._setup_ui()
        self._apply_theme()
        self.rebuild_from_config()

        self.move(self._config.window_x, self._config.window_y)

    # --- UI setup ---

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(15, 15, 15, 15)
        root.setSpacing(10)

        # --- Title Bar ---
        self._title_bar = TitleBar(self)
        self._title_bar.setObjectName("titleBar")
        self._title_bar.setFixedHeight(36)
        self._title_bar.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._title_bar.customContextMenuRequested.connect(self._show_title_context_menu)

        title_layout = QHBoxLayout(self._title_bar)
        title_layout.setContentsMargins(8, 0, 4, 0)
        title_layout.setSpacing(6)

        # Title label with stroke effect matching pokemon names
        self._title_label = StrokedLabel("精灵计数器")
        self._title_label.setStrokeWidth(3)
        self._title_label.setFillColor("#FFF8DC")
        title_layout.addWidget(self._title_label)

        title_layout.addStretch()

        # Settings gear button
        self._settings_btn = QPushButton()
        self._settings_btn.setFixedSize(25, 25)
        self._settings_btn.setToolTip("设置")
        self._settings_btn.setIconSize(QSize(16, 16))
        # Try loading icon from multiple paths, fallback to unicode gear
        icon_loaded = False
        for icon_path in _SETTINGS_ICON_PATHS:
            if os.path.exists(icon_path):
                self._settings_btn.setIcon(QIcon(icon_path))
                icon_loaded = True
                break
        if not icon_loaded:
            self._settings_btn.setText("\u2699")  # ⚙ gear unicode
        self._settings_btn.clicked.connect(self._open_settings)
        title_layout.addWidget(self._settings_btn)

        # Add button
        self._add_btn = QPushButton("+")
        self._add_btn.setFixedSize(25, 25)
        self._add_btn.setToolTip("添加精灵")
        self._add_btn.clicked.connect(self.add_pokemon)
        title_layout.addWidget(self._add_btn)

        # Opacity slider
        self._opacity_label = StrokedLabel("透明度:")
        self._opacity_label.setStrokeWidth(2)
        self._opacity_label.setFillColor("#FFF8DC")
        title_layout.addWidget(self._opacity_label)

        self._opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self._opacity_slider.setRange(20, 100)
        self._opacity_slider.setValue(int(self._config.window_opacity * 100))
        self._opacity_slider.setFixedWidth(80) # Increased width
        self._opacity_slider.valueChanged.connect(self._on_opacity_changed)
        title_layout.addWidget(self._opacity_slider)

        # Close button
        self._close_btn = QPushButton("X")
        self._close_btn.setFixedSize(25, 25) # Adjusted size
        self._close_btn.setToolTip("关闭")
        self._close_btn.clicked.connect(self.close)
        title_layout.addWidget(self._close_btn)

        root.addWidget(self._title_bar)

        # --- Scroll Area ---
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self._card_container = QWidget()
        self._card_container.setObjectName("cardContainer")
        self._card_layout = QVBoxLayout(self._card_container)
        self._card_layout.setContentsMargins(0, 0, 0, 0)
        self._card_layout.setSpacing(5)
        self._card_layout.addStretch()

        self._scroll_area.setWidget(self._card_container)
        root.addWidget(self._scroll_area)

    # --- Theme-aware styling ---

    def _apply_theme(self):
        """Apply unified golden-brown styling."""
        self._bg_pixmap = QPixmap(os.path.join(_UI_DIR, "bg_main_2.png"))
        self.setObjectName("overlay")

        # Title bar
        self._title_bar.setStyleSheet("QWidget#titleBar { background-color: transparent; }")

        # Title label
        self._title_label.setStyleSheet("background-color: transparent; font-size: 15px; color: #FFD700;")

        # Buttons
        btn_normal = "border-image: url(assets/ui/btn_bg_normal.png) 8 8 8 8 stretch stretch;"
        btn_pressed = "border-image: url(assets/ui/btn_bg_pressed.png) 8 8 8 8 stretch stretch;"

        self._settings_btn.setStyleSheet(
            f"QPushButton {{ {btn_normal} color: white; font-weight: bold; }}"
            f"QPushButton:pressed {{ {btn_pressed} }}"
        )
        self._add_btn.setStyleSheet(
            f"QPushButton {{ {btn_normal} color: white; font-weight: bold; font-size: 10px; }}"
            f"QPushButton:pressed {{ {btn_pressed} }}"
        )

        # Opacity label
        self._opacity_label.setStyleSheet("")

        # Opacity slider
        self._opacity_slider.setStyleSheet(
            "QSlider::groove:horizontal {"
            "  height: 12px;"
            "  border-image: url(assets/ui/slider_groove.png) 2 5 2 5 stretch stretch;"
            "}"
            "QSlider::handle:horizontal {"
            "  width: 12px; height: 12px;"
            "  margin: 0 0;"
            "  border-image: url(assets/ui/slider_handle.png) 0 0 0 0 stretch stretch;"
            "}"
        )

        # Close button
        self._close_btn.setStyleSheet(
            f"QPushButton {{ {btn_normal} color: white; font-weight: bold; font-size: 10px; }}"
            f"QPushButton:pressed {{ {btn_pressed} }}"
        )

        # Scroll area
        self._scroll_area.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
            "QScrollBar:vertical { width: 6px; background: #2a2a2a; border-radius: 3px; }"
            "QScrollBar::handle:vertical { background: #555555; border-radius: 3px; min-height: 20px; }"
            "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }"
        )

        # Card container
        self._card_container.setStyleSheet("QWidget#cardContainer { background-color: transparent; }")

        # Update cards
        for card in self._cards:
            card.apply_theme()

    # --- Paint background ---

    # --- 9-slice background painting ---

    # Slice values from the source image: top, right, bottom, left
    _SLICE_T = 4
    _SLICE_R = 2
    _SLICE_B = 4
    _SLICE_L = 2

    def paintEvent(self, event):
        if self._bg_pixmap.isNull():
            super().paintEvent(event)
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        src = self._bg_pixmap
        sw, sh = src.width(), src.height()
        w, h = self.width(), self.height()
        l, r, t, b = self._SLICE_L, self._SLICE_R, self._SLICE_T, self._SLICE_B

        # Source quadrants
        sx = [0, l, sw - r, sw]  # x boundaries: 0, left, sr-right, width
        sy = [0, t, sh - b, sh]  # y boundaries: 0, top, sr-bottom, height
        # Dest quadrants
        dx = [0, l, w - r, w]
        dy = [0, t, h - b, h]

        for row in range(3):
            for col in range(3):
                src_rect = QPixmap.copy(
                    src,
                    sx[col], sy[row],
                    sx[col + 1] - sx[col],
                    sy[row + 1] - sy[row],
                )
                dest_rect = (
                    dx[col], dy[row],
                    dx[col + 1] - dx[col],
                    dy[row + 1] - dy[row],
                )
                painter.drawPixmap(*dest_rect, src_rect)

        super().paintEvent(event)

    # --- Drag to move ---

    # --- Opacity ---

    def _on_opacity_changed(self, value: int):
        opacity = value / 100.0
        self._config.window_opacity = opacity
        self.setWindowOpacity(opacity)

    # --- Settings ---

    def _open_settings(self):
        """Open the settings dialog."""
        from views.settings_dialog import SettingsDialog
        dlg = SettingsDialog(self._app_state, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            # Apply display settings
            new_opacity = dlg.get_opacity()
            new_width = dlg.get_width()

            self._config.window_opacity = new_opacity
            self._config.window_width = new_width

            self.setWindowOpacity(new_opacity)
            self.setFixedWidth(new_width)
            self._opacity_slider.setValue(int(new_opacity * 100))
            self._apply_theme()

            # If pokemon list changed, rebuild cards
            if dlg.pokemon_changed():
                self.rebuild_from_config()

            self._app_state._schedule_save()
            self.settings_changed.emit()

    # --- Title bar context menu ---

    def _show_title_context_menu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet(
            "QMenu {"
            "  background-color: #2d2d2d;"
            "  color: #d0d0d0;"
            "  border: 1px solid #444444;"
            "  border-radius: 4px;"
            "  padding: 4px;"
            "}"
            "QMenu::item {"
            "  padding: 6px 20px;"
            "  border-radius: 3px;"
            "}"
            "QMenu::item:selected {"
            "  background-color: #3a3a3a;"
            "}"
        )

        add_action = QAction("添加精灵...", self)
        add_action.triggered.connect(self.add_pokemon)
        menu.addAction(add_action)

        sett_action = QAction("设置...", self)
        sett_action.triggered.connect(self._open_settings)
        menu.addAction(sett_action)

        menu.exec_(self.mapToGlobal(pos))

    # --- Card management ---

    def add_pokemon(self):
        """Open config dialog to add a new pokemon."""
        from views.config_dialog import ConfigDialog
        dlg = ConfigDialog(parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            entry = dlg.get_pokemon_entry()
            self._config.pokemon.append(entry)
            self.rebuild_from_config()
            self._app_state._schedule_save()
        self.add_pokemon_requested.emit()

    def edit_pokemon(self, pokemon_id: str):
        """Open config dialog to edit an existing pokemon."""
        from views.config_dialog import ConfigDialog
        entry = self._app_state.get_pokemon(pokemon_id)
        if entry is None:
            return
        dlg = ConfigDialog(entry, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            entry = dlg.get_pokemon_entry()
            self.rebuild_from_config()
            self._app_state._schedule_save()
        self.edit_pokemon_requested.emit(pokemon_id)

    def remove_pokemon(self, pokemon_id: str):
        """Remove a pokemon from tracking."""
        self._config.pokemon = [
            p for p in self._config.pokemon if p.id != pokemon_id
        ]
        self.rebuild_from_config()
        self._app_state._schedule_save()
        self.remove_pokemon_requested.emit(pokemon_id)

    def refresh_cards(self):
        """Update all currently displayed cards."""
        for card in self._cards:
            card.refresh_image()
            card.update_count_display(card._pokemon_data.count)

    def rebuild_from_config(self):
        """Clear and rebuild all PokemonCard widgets from config."""
        for card in self._cards:
            card.deleteLater()
        self._cards.clear()

        while self._card_layout.count():
            item = self._card_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        for entry in self._config.pokemon:
            if not entry.enabled:
                continue
            card = PokemonCard(
                entry, self._app_state, self._config.thumbnail_size
            )
            card.edit_requested.connect(self.edit_pokemon)
            card.remove_requested.connect(self.remove_pokemon)
            self._cards.append(card)
            self._card_layout.addWidget(card)

        self._card_layout.addStretch()

        # Cap window height
        screen = QApplication.primaryScreen()
        if screen:
            screen_height = screen.availableGeometry().height()
            max_height = int(screen_height * 0.70)
            card_count = max(len(self._cards), 1)  # at least 1 card height
            total_height = (
                60
                + card_count * (self._config.card_height + 5)
                + 20
            )
            self.setFixedHeight(min(total_height, max_height))

    # --- Close event ---

    def closeEvent(self, event):
        self._config.window_x = self.x()
        self._config.window_y = self.y()
        super().closeEvent(event)
