import typing
import logging
import ipaddress
import socket
import ping3
import paramiko
from abc import ABC
from ..domain import Host
from ..repository import IHostsRepository, HostsRepository


class IDiscoveryService(ABC):
    def scan_hosts(
            self,
            hosts: typing.Iterable[typing.Union[ipaddress.IPv4Address, ipaddress.IPv6Address]],
            ports: typing.List[range],
            timeout: int = 4
    ) -> typing.List[Host]:
        """
        Поиск хостов по сетям

        :param hosts: список сканируемых адресов
        :param ports: проверяемые на указанных адресах порты
        :param timeout:
        :return: список найденных хостов с портами, которые открыты
        """
        raise NotImplementedError

    def assert_hosts(self, hosts: typing.List[Host]) -> None:
        """
        Сравнить список хостов с хранимыми данными

        :param hosts: проверяемый список хостов
        """
        raise NotImplementedError


class IUserDiscoveryService(ABC):
    def supports(self, host: Host) -> bool:
        """
        Поддерживает ли сервис указанный хост

        :param host: проверяемый хост
        :return: True - хост поддерживается для проверки, False - не поддерживается
        """
        raise NotImplementedError

    def discover_users(self, host: Host) -> typing.Iterable[str]:
        """
        Найти пользователей на указанном хосте

        :param host: проверяемый хост
        :return: список логинов пользователей на указанном хосте
        """
        raise NotImplementedError


class DiscoveryServiceImpl(IDiscoveryService):
    def __init__(self, hosts_repository: IHostsRepository) -> None:
        self.hosts_repository = hosts_repository
        self.logger = logging.getLogger(__name__)

    def __scan_host_port(self, sock: typing.Tuple[str, int], timeout: typing.Optional[int] = None) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if timeout:
                s.settimeout(timeout)
            result = s.connect_ex(sock)
            result = result == 0
            self.logger.debug("%s: port %i is %s", sock[0], sock[1], "open" if result else "closed")
            return result

    def scan_hosts(
            self,
            hosts: typing.Iterable[typing.Union[ipaddress.IPv4Address, ipaddress.IPv6Address]],
            ports: typing.List[range],
            timeout: int = 4
    ) -> typing.List[Host]:
        self.logger.debug("Started host scanning; timeout is %i", timeout)
        socket.setdefaulttimeout(timeout)

        result = []
        for host in hosts:
            address = str(host)
            self.logger.debug("Scanning %s address", address)
            delay = ping3.ping(dest_addr=address, timeout=timeout)
            if delay is None:
                self.logger.debug("%s: no ping response", address)
                continue
            self.logger.debug("%s: got ping response", address)
            host_ports = []
            for ports_range in ports:
                host_ports.extend(filter(lambda port: self.__scan_host_port((address, port)), ports_range))
            result.append(Host(address, host_ports))
        self.logger.info("Port scanning is finished. %i hosts found", len(result))
        return result

    def __assert_ports(self, expected_host: Host, actual: typing.List[int]):
        actual = set(actual)
        expected = set(expected_host.ports)

        ports_diff = expected - actual

        if ports_diff:
            print("Following expected ports are not found for host \"{}\" ({}): {}".format(
                expected_host.name,
                expected_host.address,
                ports_diff
            ))

        ports_diff = actual - expected
        if ports_diff:
            print("Additional port found for host \"{}\" ({}): {}".format(
                expected_host.name,
                expected_host.address,
                ports_diff
            ))
        pass

    def assert_hosts(self, hosts: typing.List[Host]):
        checked_addresses = []

        for host in hosts:
            address = host.address
            checked_addresses.append(address)
            expected_host = self.hosts_repository.find_by_address(address)
            if expected_host:
                self.__assert_ports(expected_host, host.ports)
            else:
                print("New host found:\n\t{}".format(host))

        for host in self.hosts_repository.find_by_address_not_in(checked_addresses):
            print("Host not found:\n\t{}".format(host))


class SshLinuxUserDiscoveryServiceImpl(IUserDiscoveryService):

    def __init__(self) -> None:
        super().__init__()
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def supports(self, host: Host) -> bool:
        return 'Linux' == host.platform and host.ssh_port is not None

    def discover_users(self, host: Host) -> typing.Iterable[str]:
        stdin, stdout, stderr = self.client.exec_command("cut -d: -f1 /etc/passwd")
        result = stdout.read().decode()
        return result.split('\n')


DiscoveryService = DiscoveryServiceImpl(HostsRepository)  # type: IDiscoveryService
UserDiscoveryService = [SshLinuxUserDiscoveryServiceImpl()]  # type: typing.Iterable[IUserDiscoveryService]
