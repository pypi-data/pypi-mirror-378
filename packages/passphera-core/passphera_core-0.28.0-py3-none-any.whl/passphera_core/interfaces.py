from abc import ABC, abstractmethod
from uuid import UUID

from passphera_core.entities import Password, Generator


class VaultRepository(ABC):
    @abstractmethod
    def save(self, password: Password) -> None:
        pass

    @abstractmethod
    def get(self, context: str) -> Password:
        pass

    @abstractmethod
    def update(self, password: Password) -> None:
        pass

    @abstractmethod
    def delete(self, password: Password) -> None:
        pass

    @abstractmethod
    def list(self) -> list[Password]:
        pass

    @abstractmethod
    def flush(self) -> None:
        pass


class GeneratorRepository(ABC):
    @abstractmethod
    def save(self, generator: Generator) -> None:
        pass

    @abstractmethod
    def get(self, id: UUID) -> Generator:
        pass

    @abstractmethod
    def update(self, generator: Generator) -> None:
        pass
