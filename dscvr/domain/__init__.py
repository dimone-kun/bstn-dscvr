import typing


class Host:
    def __init__(self, name: str, address: str, ports: typing.List[int]):
        self.__name = name
        self.__address = address
        self.__ports = ports

    @property
    def name(self) -> str:
        return self.__name

    @property
    def address(self):
        return self.__address

    @property
    def ports(self):
        return self.__ports

    def __repr__(self) -> str:
        return "{}: {}@{}".format(self.name, self.ports, self.address)
