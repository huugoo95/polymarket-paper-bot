from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass
class PolymarketCredentials:
    api_key: str | None = None
    api_secret: str | None = None
    passphrase: str | None = None


def load_credentials() -> PolymarketCredentials:
    """
    Loads credentials from file path in POLYMARKET_CREDENTIALS_FILE.
    Expected file format (KEY=VALUE):
      POLYMARKET_API_KEY=...
      POLYMARKET_API_SECRET=...
      POLYMARKET_PASSPHRASE=...
    """
    path = os.getenv("POLYMARKET_CREDENTIALS_FILE")
    if not path:
        return PolymarketCredentials()

    p = Path(path)
    if not p.exists():
        return PolymarketCredentials()

    data: dict[str, str] = {}
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        data[k.strip()] = v.strip().strip('"').strip("'")

    return PolymarketCredentials(
        api_key=data.get("POLYMARKET_API_KEY"),
        api_secret=data.get("POLYMARKET_API_SECRET"),
        passphrase=data.get("POLYMARKET_PASSPHRASE"),
    )
