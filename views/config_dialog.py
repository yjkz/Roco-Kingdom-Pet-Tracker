import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QCheckBox,
    QDialogButtonBox,
    QFileDialog,
)

from models.pokemon_data import PokemonEntry
from core.theme import get_theme, build_dialog_style


class ConfigDialog(QDialog):
    """Dialog for adding or editing a single PokemonEntry."""

    def __init__(self, pokemon_entry: PokemonEntry = None, parent=None):
        super().__init__(parent)
        self._pokemon_entry = pokemon_entry

        self._is_new = pokemon_entry is None
        if self._is_new:
            self._pokemon_entry = PokemonEntry()
            self._pokemon_entry.enabled = False  # 默认不显示在窗口

        self.setWindowTitle("添加精灵" if self._is_new else "编辑精灵")
        self.setMinimumWidth(380)
        self.setModal(True)

        self._setup_ui()
        self._populate_fields()
        self._apply_theme()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(12)

        # Form
        form = QFormLayout()
        form.setSpacing(8)

        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("输入精灵名称...")
        self._name_edit.setMinimumWidth(200)
        form.addRow("名称:", self._name_edit)

        # Image path row
        img_row = QHBoxLayout()
        self._image_edit = QLineEdit()
        self._image_edit.setPlaceholderText("图片文件路径...")
        img_row.addWidget(self._image_edit)

        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self._on_browse)
        img_row.addWidget(browse_btn)
        form.addRow("图片:", img_row)

        # Display toggle
        self._enabled_check = QCheckBox("在悬浮窗上显示")
        form.addRow("", self._enabled_check)

        root.addLayout(form)

        # Preview
        preview_layout = QHBoxLayout()
        preview_layout.addStretch()
        self._preview_label = QLabel()
        self._preview_label.setFixedSize(48, 48)
        self._preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview_label.setStyleSheet(
            "border: 1px solid rgba(128,128,128,100); border-radius: 4px;"
        )
        preview_layout.addWidget(self._preview_label)
        preview_layout.addStretch()
        root.addLayout(preview_layout)

        # OK / Cancel
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        root.addWidget(button_box)

    def _populate_fields(self):
        self._name_edit.setText(self._pokemon_entry.name)
        self._image_edit.setText(self._pokemon_entry.image_path)
        self._enabled_check.setChecked(self._pokemon_entry.enabled)
        self._update_preview(self._pokemon_entry.image_path)
        self._image_edit.textChanged.connect(self._update_preview)

    def _on_browse(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择精灵图片",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp);;All Files (*)",
        )
        if file_path:
            self._image_edit.setText(file_path)

    def _update_preview(self, path: str):
        if path and os.path.exists(path):
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    48,
                    48,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self._preview_label.setPixmap(scaled)
                return
        self._preview_label.clear()
        self._preview_label.setText("无图片")

    def _apply_theme(self):
        t = get_theme("dark")
        self.setStyleSheet(build_dialog_style(t))

    def get_pokemon_entry(self) -> PokemonEntry:
        """Return the pokemon entry with any edits applied."""
        self._pokemon_entry.name = self._name_edit.text().strip()
        self._pokemon_entry.image_path = self._image_edit.text().strip()
        self._pokemon_entry.enabled = self._enabled_check.isChecked()
        return self._pokemon_entry
