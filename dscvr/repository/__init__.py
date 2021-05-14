import typing
import json
from abc import ABC
from ..domain import Host


class IHostsRepository(ABC):
    def find_by_address(self, address: str) -> typing.Optional[Host]:
        raise NotImplementedError()

    def find_by_address_not_in(self, address: typing.List[str]) -> typing.List[Host]:
        raise NotImplementedError()

    def find_all(self) -> typing.List[Host]:
        raise NotImplementedError()


class __HostsRepositoryJsonFileImpl(IHostsRepository):
    def __init__(self, json_file: str) -> None:
        with open(json_file, "r") as hosts_file:
            self.items = json.load(hosts_file, object_hook=lambda d: Host(**d))

    def find_all(self) -> typing.List[Host]:
        return self.items

    def find_by_address(self, address: str) -> typing.Optional[Host]:
        return next(filter(lambda i: address == i.address, self.items), None)

    def find_by_address_not_in(self, address: typing.List[str]) -> typing.List[Host]:
        return list(filter(lambda i: i.address not in address, self.items))


HostsRepository = __HostsRepositoryJsonFileImpl("./data.example.json")  # type: IHostsRepository
