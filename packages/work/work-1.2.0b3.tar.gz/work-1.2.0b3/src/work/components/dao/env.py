"""The DAO for the environment."""

import os


def get_bool(key: str, default: bool = False) -> bool:
    env_value: str | None = os.getenv(key)
    if env_value is None:
        return default
    return env_value.casefold() == "true"
