from PySide6.QtCore import QObject, Signal, QTimer
from models.pokemon_data import AppConfig
from core.persistence import save_config


class AppState(QObject):
    config_changed = Signal()
    count_changed = Signal(str, int)

    def __init__(self, config: AppConfig):
        super().__init__()
        self.config = config
        self._save_timer = QTimer()
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(500)
        self._save_timer.timeout.connect(self._do_save)

    def get_pokemon(self, pokemon_id: str):
        for p in self.config.pokemon:
            if p.id == pokemon_id:
                return p
        return None

    def increment(self, pokemon_id: str):
        for p in self.config.pokemon:
            if p.id == pokemon_id:
                p.count += 1
                self.count_changed.emit(p.id, p.count)
                self._schedule_save()
                return

    def decrement(self, pokemon_id: str):
        for p in self.config.pokemon:
            if p.id == pokemon_id and p.count > 0:
                p.count -= 1
                self.count_changed.emit(p.id, p.count)
                self._schedule_save()
                return

    def reset_count(self, pokemon_id: str):
        for p in self.config.pokemon:
            if p.id == pokemon_id:
                p.count = 0
                self.count_changed.emit(p.id, p.count)
                self._schedule_save()
                return

    def _schedule_save(self):
        self._save_timer.start()

    def _do_save(self):
        save_config(self.config)
