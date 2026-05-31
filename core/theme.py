"""Theme system with dark/light color palettes and stylesheet builders."""

THEMES = {
    "dark": {
        "overlay_bg": "#2a2a2a",
        "card_bg": "#353535",
        "card_hover_bg": "#404040",
        "text_primary": "#d0d0d0",
        "text_secondary": "rgba(200,200,200,180)",
        "text_dim": "rgba(180,180,180,140)",
        "count_color": "#FFD700",
        "title_color": "#e0e0e0",
        "button_bg": "#3a3a3a",
        "button_hover": "#4a4a4a",
        "button_pressed": "#555555",
        "reset_bg": "#3a3a3a",
        "reset_hover": "#4a4a4a",
        "add_btn_bg": "#3a3a3a",
        "add_btn_hover": "#4a4a4a",
        "close_btn_bg": "#3a3a3a",
        "close_btn_hover": "#4a4a4a",
        "settings_btn_bg": "#3a3a3a",
        "settings_btn_hover": "#4a4a4a",
        "scrollbar_bg": "#2a2a2a",
        "scrollbar_handle": "#555555",
        "menu_bg": "#2d2d2d",
        "menu_border": "#444444",
        "menu_hover": "#3a3a3a",
        "img_border": "#444444",
        "dialog_bg": "#2d2d2d",
        "dialog_text": "#d0d0d0",
        "input_bg": "#3a3a3a",
        "input_text": "#d0d0d0",
        "slider_groove": "#3a3a3a",
        "slider_handle": "#666666",
        "title_bar_bg": "#2a2a2a",
    },
    "light": {
        "overlay_bg": "rgba(240, 240, 245, 220)",
        "card_bg": "rgba(255, 255, 255, 210)",
        "card_hover_bg": "rgba(230, 230, 240, 230)",
        "text_primary": "#222222",
        "text_secondary": "rgba(0,0,0,140)",
        "text_dim": "rgba(0,0,0,100)",
        "count_color": "#B8860B",
        "title_color": "#222222",
        "button_bg": "rgba(0,0,0,12)",
        "button_hover": "rgba(0,0,0,22)",
        "button_pressed": "rgba(0,0,0,35)",
        "reset_bg": "rgba(0,0,0,10)",
        "reset_hover": "rgba(0,0,0,20)",
        "add_btn_bg": "rgba(80,160,80,190)",
        "add_btn_hover": "rgba(80,160,80,230)",
        "close_btn_bg": "rgba(210,70,70,190)",
        "close_btn_hover": "rgba(210,70,70,230)",
        "settings_btn_bg": "rgba(0,0,0,12)",
        "settings_btn_hover": "rgba(0,0,0,25)",
        "scrollbar_bg": "rgba(0,0,0,15)",
        "scrollbar_handle": "rgba(0,0,0,50)",
        "menu_bg": "rgba(250,250,252,245)",
        "menu_border": "rgba(0,0,0,20)",
        "menu_hover": "rgba(0,0,0,10)",
        "img_border": "rgba(0,0,0,30)",
        "dialog_bg": "rgba(245,245,250,248)",
        "dialog_text": "#222222",
        "input_bg": "rgba(0,0,0,8)",
        "input_text": "#222222",
        "slider_groove": "rgba(0,0,0,30)",
        "slider_handle": "rgba(0,0,0,180)",
        "title_bar_bg": "transparent",
    },
}


def get_theme(theme_name: str) -> dict:
    """Return theme color dict, falls back to dark if name unknown."""
    return THEMES.get(theme_name, THEMES["dark"])


def build_dialog_style(theme: dict) -> str:
    return (
        f"QDialog {{"
        f"  background-color: {theme['dialog_bg']};"
        f"  color: {theme['dialog_text']};"
        f"}}"
        f"QLabel {{"
        f"  color: {theme['dialog_text']};"
        f"}}"
        f"QLineEdit {{"
        f"  background-color: {theme['input_bg']};"
        f"  color: {theme['input_text']};"
        f"  border: 1px solid {theme['menu_border']};"
        f"  border-radius: 4px;"
        f"  padding: 4px 8px;"
        f"}}"
        f"QPushButton {{"
        f"  background-color: {theme['button_bg']};"
        f"  color: {theme['text_primary']};"
        f"  border: none;"
        f"  border-radius: 4px;"
        f"  padding: 6px 14px;"
        f"}}"
        f"QPushButton:hover {{"
        f"  background-color: {theme['button_hover']};"
        f"}}"
        f"QGroupBox {{"
        f"  color: {theme['text_primary']};"
        f"  border: 1px solid {theme['menu_border']};"
        f"  border-radius: 6px;"
        f"  margin-top: 8px;"
        f"  padding-top: 16px;"
        f"}}"
        f"QGroupBox::title {{"
        f"  subcontrol-origin: margin;"
        f"  left: 10px;"
        f"  padding: 0 4px;"
        f"}}"
        f"QListWidget {{"
        f"  background-color: {theme['input_bg']};"
        f"  color: {theme['dialog_text']};"
        f"  border: 1px solid {theme['menu_border']};"
        f"  border-radius: 4px;"
        f"}}"
        f"QListWidget::item:selected {{"
        f"  background-color: {theme['button_hover']};"
        f"}}"
        f"QTabWidget::pane {{"
        f"  background-color: {theme['dialog_bg']};"
        f"  border: 1px solid {theme['menu_border']};"
        f"  border-radius: 4px;"
        f"}}"
        f"QTabBar::tab {{"
        f"  background-color: {theme['button_bg']};"
        f"  color: {theme['text_primary']};"
        f"  padding: 6px 16px;"
        f"  border-top-left-radius: 4px;"
        f"  border-top-right-radius: 4px;"
        f"}}"
        f"QTabBar::tab:selected {{"
        f"  background-color: {theme['button_hover']};"
        f"}}"
        f"QSlider::groove:horizontal {{"
        f"  height: 4px;"
        f"  background: {theme['slider_groove']};"
        f"  border-radius: 2px;"
        f"}}"
        f"QSlider::handle:horizontal {{"
        f"  width: 10px; height: 10px;"
        f"  margin: -3px 0;"
        f"  background: {theme['slider_handle']};"
        f"  border-radius: 5px;"
        f"}}"
        f"QRadioButton {{"
        f"  color: {theme['dialog_text']};"
        f"}}"
    )
