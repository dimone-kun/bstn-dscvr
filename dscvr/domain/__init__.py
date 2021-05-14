import typing


class Host:
    def __init__(self, address: str, ports: typing.List[int], name: typing.Optional[str] = "Unknown"):
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
        return "{} ({}:{})".format(self.name, self.address, self.ports)
