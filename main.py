import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont, QFontDatabase
from core.persistence import ensure_dirs, load_config, save_config
from core.app_state import AppState
from views.overlay_window import OverlayWindow


def main():
    app = QApplication(sys.argv)

    # In frozen mode, chdir to _internal so CSS and __file__ paths resolve
    if getattr(sys, 'frozen', False):
        os.chdir(os.path.join(os.path.dirname(sys.executable), '_internal'))

    # Load custom font
    font_path = "fonts/猫啃网糖圆体.ttf"
    if os.path.exists(font_path):
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id >= 0:
            families = QFontDatabase.applicationFontFamilies(font_id)
            if families:
                font = QFont(families[0], 10)
                app.setFont(font)

    app.setQuitOnLastWindowClosed(False)

    ensure_dirs()
    config = load_config()
    state = AppState(config)
    window = OverlayWindow(state)

    app.aboutToQuit.connect(lambda: save_config(state.config))

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
