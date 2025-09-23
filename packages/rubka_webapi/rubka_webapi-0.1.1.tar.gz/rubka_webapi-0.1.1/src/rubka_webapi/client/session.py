
import json
from pathlib import Path
from typing import Optional
from rubka_webapi.exceptions import InvalidSessionError
from rubka_webapi.types.models import AuthData

class SessionManager:
    def __init__(self, session_name: str, session_dir: Path = Path(".")):
        self.session_name = session_name
        self.session_dir = session_dir
        self.session_file = self.session_dir / f"{session_name}.json"
        self._auth_data: Optional[AuthData] = None

    def _ensure_session_dir(self):
        self.session_dir.mkdir(parents=True, exist_ok=True)

    def save_session(self, auth_data: AuthData):
        self._ensure_session_dir()
        with open(self.session_file, "w", encoding="utf-8") as f:
            f.write(auth_data.model_dump_json(indent=4))
        self._auth_data = auth_data

    def load_session(self) -> AuthData:
        if not self.session_file.exists():
            raise InvalidSessionError(f"Session file not found: {self.session_file}")
        try:
            with open(self.session_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._auth_data = AuthData(**data)
            return self._auth_data
        except (json.JSONDecodeError, KeyError) as e:
            raise InvalidSessionError(f"Invalid session file format: {e}") from e

    def get_auth_data(self) -> Optional[AuthData]:
        return self._auth_data

    def session_exists(self) -> bool:
        return self.session_file.exists()

    def delete_session(self):
        if self.session_file.exists():
            self.session_file.unlink()
            self._auth_data = None


