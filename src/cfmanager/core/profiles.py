import json
from pathlib import Path
from typing import Any, Dict, Optional

from cfmanager.core.exceptions import CFManagerError


class ProfileError(CFManagerError):
    pass


class ProfileManager:
    _DEFAULT_FILE: Path = Path.home() / ".cfmanager" / "profiles.json"

    def __init__(self, profiles_file: Optional[Path] = None):
        self._path = Path(profiles_file) if profiles_file else self._DEFAULT_FILE

    def _load(self) -> Dict[str, Any]:
        if not self._path.exists():
            return {}
        return json.loads(self._path.read_text())

    def _save(self, data: Dict[str, Any]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(data, indent=2))
        self._path.chmod(0o600)

    def list_profiles(self) -> Dict[str, Any]:
        return self._load()

    def get(self, name: str) -> Dict[str, Any]:
        profiles = self._load()
        if name not in profiles:
            raise ProfileError(f"Profile '{name}' not found.")
        return profiles[name]

    def add(self, name: str, api_token: str, account_id: Optional[str] = None) -> None:
        profiles = self._load()
        entry: Dict[str, Any] = {"api_token": api_token}
        if account_id:
            entry["account_id"] = account_id
        profiles[name] = entry
        self._save(profiles)

    def delete(self, name: str) -> None:
        profiles = self._load()
        if name not in profiles:
            raise ProfileError(f"Profile '{name}' not found.")
        del profiles[name]
        self._save(profiles)
