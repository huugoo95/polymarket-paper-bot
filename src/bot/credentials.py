from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass
class PolymarketCredentials:
    private_key: str | None = None
    wallet_address: str | None = None


def load_credentials() -> PolymarketCredentials:
    """
    Loads credentials from file path in POLYMARKET_CREDENTIALS_FILE.
    Expected file format (KEY=VALUE):
      POLYMARKET_PRIVATE_KEY=...
      POLYMARKET_WALLET_ADDRESS=...
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
        private_key=data.get("POLYMARKET_PRIVATE_KEY"),
        wallet_address=data.get("POLYMARKET_WALLET_ADDRESS"),
    )
