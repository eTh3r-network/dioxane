from abc import ABC, abstractmethod

from models.identity import Identity


class IdentityProvider(ABC):
    @staticmethod
    @abstractmethod
    def getIdentity(identity: str) -> Identity:
        pass
