from typing import Any


class InvalidRefException(Exception):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
