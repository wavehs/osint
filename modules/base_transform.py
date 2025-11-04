from abc import ABC, abstractmethod
from models import BaseEntity
from typing import List

class BaseTransform(ABC):
    """
    Abstract base class for all transforms.
    """
    def __init__(self, investigation_id: int):
        self.investigation_id = investigation_id

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the transform."""
        pass

    @abstractmethod
    async def run(self, entity: BaseEntity) -> str:
        """
        Runs the transform on the given entity.
        Returns the raw output of the tool.
        """
        pass

    @abstractmethod
    def parse(self, raw_output: str) -> List[BaseEntity]:
        """
        Parses the raw output of the transform and returns a list of new entities.
        """
        pass
