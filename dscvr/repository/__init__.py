import typing
import logging
import json
from abc import ABC, abstractmethod
from ..domain import Host


class IHostsRepository(ABC):
    @abstractmethod
    def find_by_address(self, address: str) -> typing.Optional[Host]:
        raise NotImplementedError()

    @abstractmethod
    def find_by_address_not_in(self, address: typing.List[str]) -> typing.List[Host]:
        raise NotImplementedError()

    @abstractmethod
    def find_all(self) -> typing.List[Host]:
        raise NotImplementedError()


class _HostsRepositoryJsonFileImpl(IHostsRepository):
    def __init__(self, json_file: str) -> None:
        self.logger = logging.getLogger(__name__)
        with open(json_file, "r") as hosts_file:
            self.logger.debug("Loading hosts data from %s", json_file)
            self.items = json.load(hosts_file, object_hook=lambda d: Host(**d))

    def find_all(self) -> typing.List[Host]:
        return self.items

    def find_by_address(self, address: str) -> typing.Optional[Host]:
        return next(filter(lambda i: address == i.address, self.items), None)

    def find_by_address_not_in(self, address: typing.List[str]) -> typing.List[Host]:
        return list(filter(lambda i: i.address not in address, self.items))


json_source_file = "./data.example.json"
HostsRepository = _HostsRepositoryJsonFileImpl(json_source_file)  # type: IHostsRepository
