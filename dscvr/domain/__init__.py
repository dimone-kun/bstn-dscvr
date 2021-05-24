import typing


class Host:
    def __init__(self, address: str, ports: typing.List[int], name: str = "Unknown",
                 platform: typing.Optional[str] = None):
        self.__name = name
        self.__address = address
        self.__ports = ports
        self.__platform = platform

    @property
    def name(self) -> str:
        return self.__name

    @property
    def address(self):
        return self.__address

    @property
    def ports(self):
        return self.__ports

    @property
    def ssh_port(self) -> typing.Optional[int]:
        return 22 if 22 in self.ports else None

    @property
    def platform(self) -> typing.Optional[str]:
        return self.__platform

    def __repr__(self) -> str:
        return "{} ({}:{})".format(self.name, self.address, self.ports)
