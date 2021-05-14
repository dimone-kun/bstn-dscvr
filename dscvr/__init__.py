import typing
import socket
import ipaddress
import ping3


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
