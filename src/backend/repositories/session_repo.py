import json

class SessionRepository:
    def __init__(self, file: str = None) -> None:
        self.file = file or "data/sessions.json"
        try:
            with open(self.file, "r") as f:
                json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            with open(self.file, "w") as f:
                json.dump(None, f)

    def save(self, user: dict) -> None:
        with open(self.file, "w") as f:
            json.dump(user, f, indent=4, default=lambda o: o.value if hasattr(o, 'value') else str(o))

    def clear(self) -> None:
        with open(self.file, "w") as f:
            json.dump(None, f)

    def get(self) -> dict | None:
        try:
            with open(self.file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None
