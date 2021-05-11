import typing
import typing_extensions
import socket
import sys
import json
import ipaddress
import ping3

Host = typing_extensions.TypedDict("Host", {"name": str, "address": str, "ports": typing.List[int]})


def read_scan_ranges(range_arg: str) -> typing.List[range]:
    """
    Прочитать диапазон портов для сканирования из аргумента

    :param range_arg: значение аргумента командной строки
    :return: список диапазонов для сканирования
    """
    result = []
    if ',' in range_arg:
        ports_ranges = range_arg.split(',')
    else:
        ports_ranges = [range_arg]
    for ports_range in ports_ranges:
        if ':' in ports_range:
            ports_range = ports_range.split(":")
            start_port = int(ports_range[0])
            end_port = int(ports_range[1])
        else:
            start_port = int(ports_range)
            end_port = start_port
        result.append(range(start_port, end_port + 1))
    return result


def read_hosts(network_arg: str) -> typing.Set[typing.Union[ipaddress.IPv4Address, ipaddress.IPv6Address]]:
    """
    Прочитать список хостов из аргумента

    :param network_arg: значение аргумента командной строки
    :return: список хостов для сканирования
    """
    result = set()
    if ',' in network_arg:
        networks = network_arg.split(',')
    else:
        networks = [network_arg]
    for network in networks:
        if '/' in network:
            result.update(list(ipaddress.ip_network(network).hosts()))
        else:
            result.add(ipaddress.ip_address(network))
    return result


def scan_host_ports(sock: typing.Tuple[str, int], timeout: typing.Optional[int] = None):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if timeout:
            s.settimeout(timeout)
        result = s.connect_ex(sock)
        print("Port {} is {} for {}".format(sock[1], 'open' if result == 0 else 'closed', sock[0]))


if __name__ == "__main__":
    hosts = read_hosts(sys.argv[1])
    ports = read_scan_ranges(sys.argv[2])
    timeout = 4 if len(sys.argv) < 4 else int(sys.argv[3])

    socket.setdefaulttimeout(timeout)

    for host in hosts:
        address = str(host)
        delay = ping3.ping(dest_addr=address, timeout=timeout)
        if delay is None:
            print("Host {} is unavailable".format(address))
            continue
        for ports_range in ports:
            for port in ports_range:
                scan_host_ports((address, port))
