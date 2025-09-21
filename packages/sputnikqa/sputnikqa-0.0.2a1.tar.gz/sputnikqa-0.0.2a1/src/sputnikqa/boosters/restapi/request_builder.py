from copy import deepcopy
from typing import Any


class RequestDictBuilder:
    _data: dict[str, Any] = {}

    def build(self) -> dict[str, Any]:
        return deepcopy(self._data)

    def __repr__(self):
        return f'{self.__class__.__name__}({self._data})'
