"""Environment-driven database configuration (zero hardcoded credentials)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _load_dotenv_if_present(env_path: Path) -> None:
    """Minimal zero-dependency .env loader for local development."""
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


@dataclass(frozen=True)
class DatabaseConfig:
    host: str
    port: int
    user: str
    password: str
    database: str

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        repo_root = Path(__file__).resolve().parent.parent
        _load_dotenv_if_present(repo_root / ".env")
        return cls(
            host=os.getenv("HOTEL_DB_HOST", "localhost"),
            port=int(os.getenv("HOTEL_DB_PORT", "3306")),
            user=os.getenv("HOTEL_DB_USER", "root"),
            password=os.getenv("HOTEL_DB_PASSWORD", ""),
            database=os.getenv("HOTEL_DB_NAME", "hotel_booking_system"),
        )
