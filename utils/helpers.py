"""Small reusable helpers shared by UI and API tests."""
import json
from functools import lru_cache
from types import SimpleNamespace

from config import settings


@lru_cache(maxsize=1)
def load_test_data() -> dict:
    with open(settings.DATA_FILE, encoding="utf-8") as fh:
        return json.load(fh)


def ns(d: dict) -> SimpleNamespace:
    """Dict -> attribute access (data.user.username)."""
    return SimpleNamespace(**{k: ns(v) if isinstance(v, dict) else v for k, v in d.items()})
