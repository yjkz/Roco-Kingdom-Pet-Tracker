import colorsys
import hashlib

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont, QFontMetrics, QAction
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QMenu, QWidget

from models.pokemon_data import PokemonEntry
from views.components import StrokedLabel


class PokemonCard(QFrame):
    """A single pokemon row showing image, name, count, and +/-/reset buttons."""

    edit_requested = Signal(str)
    remove_requested = Signal(str)

    def __init__(self, pokemon_data: PokemonEntry, app_state, thumbnail_size: int = 48):
        super().__init__()
        self._pokemon_data = pokemon_data
        self._app_state = app_state
        self._thumbnail_size = thumbnail_size

        self.setFixedHeight(64)
        self.setObjectName("pokemonCard")
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

        self._setup_ui()
        self._connect_signals()
        self._apply_theme()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)

        # Image thumbnail / placeholder container
        self._image_container = QWidget()
        self._image_container.setFixedSize(self._thumbnail_size + 10, self._thumbnail_size + 10)
        
        self._image_label = QLabel(self._image_container)
        self._image_label.setGeometry(5, 5, self._thumbnail_size, self._thumbnail_size)
        self._image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.refresh_image()
        
        self._frame_label = QLabel(self._image_container)
        self._frame_label.setGeometry(0, 0, self._thumbnail_size + 10, self._thumbnail_size + 10)
        self._frame_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._frame_label.setStyleSheet("border-image: url(assets/ui/avatar_frame.png) 5 5 5 5 stretch stretch;")
        
        layout.addWidget(self._image_container)

        # Name label (elided)
        self._name_label = StrokedLabel()
        self._name_label.setStrokeWidth(3)
        self._name_label.setFillColor("#FFF8DC")
        self._name_label.setFixedWidth(80)
        self._name_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self._set_elided_name()
        layout.addWidget(self._name_label)

        # Count label (large, bold, gold)
        self._count_label = StrokedLabel(str(self._pokemon_data.count))
        self._count_label.setStrokeWidth(5)
        self._count_label.setFillColor("#FFD700")
        self._count_label.setFixedWidth(50)
        self._count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self._count_label.setFont(font)
        layout.addWidget(self._count_label)

        # +1 Button
        self._btn_plus = QPushButton("+")
        self._btn_plus.setToolTip("+1")
        layout.addWidget(self._btn_plus)

        # -1 Button
        self._btn_minus = QPushButton("-")
        self._btn_minus.setToolTip("-1")
        layout.addWidget(self._btn_minus)

        # Reset Button
        self._btn_reset = QPushButton("重置")
        self._btn_reset.setToolTip("重置计数为0")
        layout.addWidget(self._btn_reset)

    def _connect_signals(self):
        self._btn_plus.clicked.connect(
            lambda: self._app_state.increment(self._pokemon_data.id)
        )
        self._btn_minus.clicked.connect(
            lambda: self._app_state.decrement(self._pokemon_data.id)
        )
        self._btn_reset.clicked.connect(
            lambda: self._app_state.reset_count(self._pokemon_data.id)
        )
        self._app_state.count_changed.connect(self._on_count_changed)

    def _on_count_changed(self, pokemon_id: str, new_count: int):
        if pokemon_id == self._pokemon_data.id:
            self.update_count_display(new_count)

    def update_count_display(self, new_count: int):
        self._pokemon_data.count = new_count
        self._count_label.setText(str(new_count))

    def refresh_image(self):
        pixmap = None
        for path in [self._pokemon_data.thumbnail_path, self._pokemon_data.image_path]:
            if path:
                tmp = QPixmap(path)
                if not tmp.isNull():
                    pixmap = tmp
                    break

        if pixmap and not pixmap.isNull():
            scaled = pixmap.scaled(
                self._thumbnail_size,
                self._thumbnail_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self._image_label.setPixmap(scaled)
        else:
            self._draw_placeholder()

    def _draw_placeholder(self):
        size = self._thumbnail_size
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        color = self._name_to_color(self._pokemon_data.name)
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(4, 4, size - 8, size - 8)

        letter = (
            self._pokemon_data.name[0].upper() if self._pokemon_data.name else "?"
        )
        painter.setPen(QColor(255, 255, 255))
        font = QFont()
        font.setPointSize(size // 2)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(0, 0, size, size, Qt.AlignmentFlag.AlignCenter, letter)

        painter.end()
        self._image_label.setPixmap(pixmap)

    def _name_to_color(self, name: str) -> QColor:
        digest = hashlib.md5(name.encode()).hexdigest()
        hue = int(digest, 16) % 360
        r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(hue / 360.0, 0.7, 0.8)]
        return QColor(r, g, b)

    def _set_elided_name(self):
        fm = QFontMetrics(self._name_label.font())
        elided = fm.elidedText(
            self._pokemon_data.name, Qt.TextElideMode.ElideRight, 76
        )
        self._name_label.setText(elided)
        self._name_label.setToolTip(self._pokemon_data.name)

    # --- Theme-aware styling ---

    def _apply_theme(self, theme_name: str = None):
        """Apply unified golden-brown card styling."""

        # Frame label with avatar border
        self._frame_label.setStyleSheet(
            "border-image: url(assets/ui/avatar_frame.png) 5 5 5 5 stretch stretch;"
        )

        # Card frame - golden-brown matching UI theme
        self.setStyleSheet(
            "QFrame#pokemonCard {"
            "  background-color: #EADDBF;"
            "  border-radius: 10px;"
            "}"
            "QFrame#pokemonCard:hover {"
            "  background-color: #F5ECD8;"
            "}"
        )

        # Name label
        self._name_label.setStyleSheet(
            "font-weight: bold; font-size: 12px;"
        )

        # Count label - gold color
        self._count_label.setStyleSheet("color: #FFD700;")

        # Image label
        self._image_label.setStyleSheet("background: transparent;")

        # +/- and Reset buttons
        btn_normal = "border-image: url(assets/ui/btn_bg_normal.png) 8 8 8 8 stretch stretch;"
        btn_pressed = "border-image: url(assets/ui/btn_bg_pressed.png) 8 8 8 8 stretch stretch;"

        action_btn = (
            f"QPushButton {{"
            f"  {btn_normal}"
            f"  color: white;"
            f"  font-weight: bold;"
            f"  font-size: 14px;"
            f"  min-width: 28px; min-height: 28px;"
            f"  max-width: 28px; max-height: 28px;"
            f"}}"
            f"QPushButton:pressed {{ {btn_pressed} }}"
        )
        self._btn_plus.setStyleSheet(action_btn)
        self._btn_minus.setStyleSheet(action_btn)

        reset_btn = (
            f"QPushButton {{"
            f"  {btn_normal}"
            f"  color: white;"
            f"  font-size: 10px;"
            f"  min-width: 36px; min-height: 28px;"
            f"  max-width: 36px; max-height: 28px;"
            f"}}"
            f"QPushButton:pressed {{ {btn_pressed} }}"
        )
        self._btn_reset.setStyleSheet(reset_btn)

    def apply_theme(self, theme_name: str = None):
        """Public method for external callers to update theme."""
        self._apply_theme(theme_name)

    # --- Context menu ---

    def _show_context_menu(self, pos):
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

        edit_action = QAction("编辑...", self)
        edit_action.triggered.connect(
            lambda: self.edit_requested.emit(self._pokemon_data.id)
        )
        menu.addAction(edit_action)

        remove_action = QAction("删除", self)
        remove_action.triggered.connect(
            lambda: self.remove_requested.emit(self._pokemon_data.id)
        )
        menu.addAction(remove_action)

        menu.exec_(self.mapToGlobal(pos))
