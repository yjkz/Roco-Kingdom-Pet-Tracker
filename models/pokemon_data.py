from dataclasses import dataclass, field, asdict
import uuid


@dataclass
class PokemonEntry:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    count: int = 0
    image_path: str = ""
    thumbnail_path: str = ""
    enabled: bool = True
    sort_order: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "PokemonEntry":
        return cls(**{k: d.get(k, v) for k, v in cls().__dict__.items()})


@dataclass
class AppConfig:
    version: int = 1
    pokemon: list[PokemonEntry] = field(default_factory=list)
    window_x: int = 100
    window_y: int = 100
    window_opacity: float = 0.90
    card_height: int = 64
    thumbnail_size: int = 48
    window_width: int = 400

    def to_dict(self) -> dict:
        d = asdict(self)
        d["pokemon"] = [p.to_dict() for p in self.pokemon]
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "AppConfig":
        pokemon = [PokemonEntry.from_dict(p) for p in d.get("pokemon", [])]
        cfg = cls(**{k: v for k, v in d.items() if k != "pokemon"})
        cfg.pokemon = pokemon
        return cfg
