from dataclasses import dataclass
from typing import Any

from pyeqx.core.common import from_str
from pyeqx.core.models.storage.properties.data_properties import DataProperties


@dataclass
class LocalPathDataProperties(DataProperties):
    path: str

    def __init__(self, path):
        parsed_obj: dict = {}
        parsed_obj["path"] = path
        self.__dict__ = parsed_obj

    @staticmethod
    def from_dict(obj: Any) -> "LocalPathDataProperties":
        assert isinstance(obj, dict)
        path = from_str(obj.get("path"))
        return LocalPathDataProperties(path)

    def to_dict(self) -> dict:
        result: dict = {}
        result["path"] = from_str(self.path)
        return result

    def from_properties(self) -> "LocalPathDataProperties":
        return LocalPathDataProperties(self.path)
