import typing
import socket
import ipaddress
import ping3
from .domain import Host
from .repository import HostsRepository as repository


def __scan_host_port(sock: typing.Tuple[str, int], timeout: typing.Optional[int] = None):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if timeout:
            s.settimeout(timeout)
        result = s.connect_ex(sock)
        print("Port {} is {} for {}".format(sock[1], 'open' if result == 0 else 'closed', sock[0]))


def scan_hosts(
        hosts: typing.Iterable[typing.Union[ipaddress.IPv4Address, ipaddress.IPv6Address]],
        ports: typing.List[range],
        timeout: int = 4
):
    socket.setdefaulttimeout(timeout)

    for host in hosts:
        address = str(host)
        delay = ping3.ping(dest_addr=address, timeout=timeout)
        if delay is None:
            print("Host {} is unavailable".format(address))
            continue
        for ports_range in ports:
            for port in ports_range:
                __scan_host_port((address, port))


def __assert_ports(expected_host: Host, actual: typing.List[int]):
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


def assert_hosts(hosts: typing.List[Host]):
    checked_addresses = []

    for host in hosts:
        address = host.address
        checked_addresses.append(address)
        expected_host = repository.find_by_address(address)
        if expected_host:
            __assert_ports(expected_host, host.ports)
        else:
            print("New host found:\n\t{}".format(host))

    for host in repository.find_by_address_not_in(checked_addresses):
        print("Host not found:\n\t{}".format(host))
