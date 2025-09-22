from dataclasses import dataclass, field


@dataclass
class Password:
    context: str = field(default_factory=str)
    text: str = field(default_factory=str)
    password: str = field(default_factory=str)
    salt: bytes = field(default_factory=lambda: bytes)

    def to_dict(self) -> dict:
        """Convert the Password entity to a dictionary."""
        return {
            "context": self.context,
            "text": self.text,
            "password": self.password,
            "salt": self.salt,
        }

    def from_dict(self, data: dict) -> None:
        """Convert a dictionary to a Password entity."""
        for key, value in data.items():
            if key in ["context", "text", "password", "salt"]:
                setattr(self, key, value)
