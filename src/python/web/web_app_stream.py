from abc import ABC, abstractmethod
from typing import Optional


class WebAppStream(ABC):
    """
    Abstract class that defines a streaming data provider
    """
    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def get_value(self) -> Optional[str]:
        pass

    @abstractmethod
    def cleanup(self):
        pass
