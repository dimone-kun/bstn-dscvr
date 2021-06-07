import typing
import logging
import ipaddress
import socket
import ping3
import paramiko
import json
import inspect
from abc import ABC, abstractmethod
from ..domain import Host
from ..repository import IHostsRepository, HostsRepository


class IDiscoveryService(ABC):
    @abstractmethod
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

    @abstractmethod
    def assert_hosts(self, hosts: typing.List[Host]) -> None:
        """
        Сравнить список хостов с хранимыми данными

        :param hosts: проверяемый список хостов
        """
        raise NotImplementedError


class IUserDiscoveryService(ABC):
    @abstractmethod
    def supports(self, host: Host) -> bool:
        """
        Поддерживает ли сервис указанный хост

        :param host: проверяемый хост
        :return: True - хост поддерживается для проверки, False - не поддерживается
        """
        raise NotImplementedError

    @abstractmethod
    def discover_users(self, host: Host) -> typing.Iterable[str]:
        """
        Найти пользователей на указанном хосте

        :param host: проверяемый хост
        :return: список логинов пользователей на указанном хосте
        """
        raise NotImplementedError


class ICredentialsService(ABC):
    @abstractmethod
    def get_credentials(self, service: typing.Union[typing.Type, object], host: Host) -> dict:
        """
        :param service: сервис, который запрашивает параметры аутентификации
        :param host: хост, для которого необходимо получить параметры аутентификации
        :return: словарь аргументов для авторизации
        :raises Warning: не найдены параметры аутентификации для сервиса
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


__SshService = type('SshService', (), {})


class SshLinuxUserDiscoveryServiceImpl(IUserDiscoveryService, __SshService):

    def __init__(self, credentials_service: ICredentialsService, ssh_client: paramiko.SSHClient = None) -> None:
        super().__init__()
        if not ssh_client:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client = ssh_client
        self.credentials_service = credentials_service

    def supports(self, host: Host) -> bool:
        return 'Linux' == host.platform and host.ssh_port is not None

    def discover_users(self, host: Host) -> typing.Iterable[str]:
        creds = self.credentials_service.get_credentials(SshLinuxUserDiscoveryServiceImpl, host)
        self.client.connect(host.address, port=host.ssh_port, **creds)
        try:
            stdin, stdout, stderr = self.client.exec_command("cut -d: -f1 /etc/passwd")
            result = stdout.read().decode()
            return result.split('\n')
        finally:
            self.client.close()


class CredentialsServiceJsonFileImpl(ICredentialsService):
    def __init__(self, json_file: str) -> None:
        self.logger = logging.getLogger(__name__)
        with open(json_file, "r") as credentials_file:
            self.logger.debug("Loading credentials data from %s", json_file)
            self.items = json.load(credentials_file)

    def get_credentials(self, service: typing.Union[typing.Type, object], host: Host) -> dict:
        if not inspect.isclass(service):
            service = type(service)  # type: type

        for cls in service.mro():
            service_name = cls.__name__
            if service_name in self.items and self.items[service_name][host.address]:
                return self.items[service_name][host.address]

        raise Warning("No credentials found for {} service".format(service.__name__))


credentials_json = "./credentials.example.json"

DiscoveryService = DiscoveryServiceImpl(HostsRepository)  # type: IDiscoveryService
CredentialsService = CredentialsServiceJsonFileImpl(credentials_json)  # type: ICredentialsService
UserDiscoveryService = [SshLinuxUserDiscoveryServiceImpl(CredentialsService)]  # type: typing.Iterable[IUserDiscoveryService]
