import copy

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QListWidget,
    QListWidgetItem,
    QTabWidget,
    QWidget,
    QDialogButtonBox,
    QMessageBox,
    QGroupBox,
)

from core.theme import get_theme, build_dialog_style


class SettingsDialog(QDialog):
    """2-tab settings dialog for Pokemon management and display."""

    def __init__(self, app_state, parent=None):
        super().__init__(parent)
        self._app_state = app_state
        self._config = app_state.config
        self._backup_config = copy.deepcopy(app_state.config)
        self._pokemon_changed = False

        self.setWindowTitle("设置")
        self.setMinimumWidth(420)
        self.setMinimumHeight(400)
        self.setModal(True)

        self._setup_ui()
        self._load_current_values()
        self._apply_dialog_theme()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setSpacing(12)

        tabs = QTabWidget()
        tabs.addTab(self._create_pokemon_tab(), "精灵管理")
        tabs.addTab(self._create_display_tab(), "显示设置")
        root.addWidget(tabs)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        root.addWidget(button_box)

    # --- Tab 1: Pokemon Management ---

    def _create_pokemon_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(8)

        self._pokemon_list = QListWidget()
        self._pokemon_list.setMinimumHeight(180)
        layout.addWidget(self._pokemon_list)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)

        add_btn = QPushButton("添加")
        add_btn.clicked.connect(self._on_add_pokemon)
        btn_row.addWidget(add_btn)

        self._edit_btn = QPushButton("编辑")
        self._edit_btn.clicked.connect(self._on_edit_pokemon)
        btn_row.addWidget(self._edit_btn)

        self._remove_btn = QPushButton("删除")
        self._remove_btn.clicked.connect(self._on_remove_pokemon)
        btn_row.addWidget(self._remove_btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)

        self._pokemon_list.itemChanged.connect(self._on_item_checked)
        self._refresh_pokemon_list()
        self._pokemon_list.currentRowChanged.connect(
            lambda _: self._update_button_states()
        )
        self._update_button_states()

        return tab

    def _refresh_pokemon_list(self):
        self._pokemon_list.blockSignals(True)
        self._pokemon_list.clear()
        for entry in self._config.pokemon:
            status = "显示" if entry.enabled else "隐藏"
            item = QListWidgetItem(
                f"{entry.name}  ({entry.count})  [{status}]"
            )
            item.setData(Qt.ItemDataRole.UserRole, entry.id)
            item.setFlags(
                item.flags() | Qt.ItemFlag.ItemIsUserCheckable
            )
            item.setCheckState(
                Qt.CheckState.Checked if entry.enabled else Qt.CheckState.Unchecked
            )
            if not entry.enabled:
                item.setForeground(Qt.GlobalColor.gray)
            self._pokemon_list.addItem(item)
        self._pokemon_list.blockSignals(False)

    def _on_item_checked(self, item):
        pokemon_id = item.data(Qt.ItemDataRole.UserRole)
        entry = self._app_state.get_pokemon(pokemon_id)
        if entry is None:
            return
        entry.enabled = (item.checkState() == Qt.CheckState.Checked)
        self._pokemon_changed = True
        self._pokemon_list.blockSignals(True)
        status = "显示" if entry.enabled else "隐藏"
        item.setText(f"{entry.name}  ({entry.count})  [{status}]")
        if not entry.enabled:
            item.setForeground(Qt.GlobalColor.gray)
        else:
            item.setForeground(Qt.GlobalColor.white)
        self._pokemon_list.blockSignals(False)

    def _update_button_states(self):
        has_selection = self._pokemon_list.currentRow() >= 0
        self._edit_btn.setEnabled(has_selection)
        self._remove_btn.setEnabled(has_selection)

    def _on_add_pokemon(self):
        from views.config_dialog import ConfigDialog
        dlg = ConfigDialog(parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            entry = dlg.get_pokemon_entry()
            self._config.pokemon.append(entry)
            self._refresh_pokemon_list()
            self._pokemon_changed = True

    def _on_edit_pokemon(self):
        item = self._pokemon_list.currentItem()
        if item is None:
            return
        pokemon_id = item.data(Qt.ItemDataRole.UserRole)
        entry = self._app_state.get_pokemon(pokemon_id)
        if entry is None:
            return
        from views.config_dialog import ConfigDialog
        dlg = ConfigDialog(entry, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            entry = dlg.get_pokemon_entry()
            self._refresh_pokemon_list()
            self._pokemon_changed = True

    def _on_remove_pokemon(self):
        item = self._pokemon_list.currentItem()
        if item is None:
            return
        pokemon_id = item.data(Qt.ItemDataRole.UserRole)
        entry = self._app_state.get_pokemon(pokemon_id)
        if entry is None:
            return
        reply = QMessageBox.question(
            self,
            "移除精灵",
            f'确认将"{entry.name}"从追踪列表中移除？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._config.pokemon = [
                p for p in self._config.pokemon if p.id != pokemon_id
            ]
            self._refresh_pokemon_list()
            self._pokemon_changed = True

    # --- Tab 2: Display Settings ---

    def _create_display_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(16)

        opacity_group = QGroupBox("窗口透明度")
        opacity_layout = QVBoxLayout(opacity_group)
        opacity_row = QHBoxLayout()
        self._opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self._opacity_slider.setRange(20, 100)
        opacity_row.addWidget(self._opacity_slider)
        self._opacity_label = QLabel("85%")
        self._opacity_label.setFixedWidth(40)
        self._opacity_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        opacity_row.addWidget(self._opacity_label)
        self._opacity_slider.valueChanged.connect(
            lambda v: self._opacity_label.setText(f"{v}%")
        )
        opacity_layout.addLayout(opacity_row)
        layout.addWidget(opacity_group)

        width_group = QGroupBox("窗口宽度")
        width_layout = QVBoxLayout(width_group)
        width_row = QHBoxLayout()
        self._width_slider = QSlider(Qt.Orientation.Horizontal)
        self._width_slider.setRange(280, 500)
        width_row.addWidget(self._width_slider)
        self._width_label = QLabel("320px")
        self._width_label.setFixedWidth(45)
        self._width_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        width_row.addWidget(self._width_label)
        self._width_slider.valueChanged.connect(
            lambda v: self._width_label.setText(f"{v}px")
        )
        width_layout.addLayout(width_row)
        layout.addWidget(width_group)

        reset_group = QGroupBox("计数")
        reset_layout = QVBoxLayout(reset_group)
        reset_btn = QPushButton("重置所有计数为零")
        reset_btn.clicked.connect(self._on_reset_all_counts)
        reset_layout.addWidget(reset_btn)
        layout.addWidget(reset_group)

        layout.addStretch()
        return tab

    def _on_reset_all_counts(self):
        reply = QMessageBox.warning(
            self,
            "重置所有计数",
            "这将把所有精灵的计数归零。\n此操作不可撤销。\n\n确认继续？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            for entry in self._config.pokemon:
                entry.count = 0
            self._refresh_pokemon_list()

    # --- Load and get values ---

    def _apply_dialog_theme(self):
        t = get_theme("dark")
        self.setStyleSheet(build_dialog_style(t))

    def accept(self):
        """Accept in-place mutations silently."""
        super().accept()

    def reject(self):
        """Restore original config from backup on Cancel."""
        self._config.pokemon = self._backup_config.pokemon
        self._config.window_opacity = self._backup_config.window_opacity
        self._config.window_width = self._backup_config.window_width
        super().reject()

    def _load_current_values(self):
        opacity_pct = int(self._config.window_opacity * 100)
        self._opacity_slider.setValue(opacity_pct)
        self._opacity_label.setText(f"{opacity_pct}%")

        width = getattr(self._config, "window_width", 320)
        self._width_slider.setValue(width)
        self._width_label.setText(f"{width}px")

    def get_opacity(self) -> float:
        return self._opacity_slider.value() / 100.0

    def get_width(self) -> int:
        return self._width_slider.value()

    def pokemon_changed(self) -> bool:
        return self._pokemon_changed
