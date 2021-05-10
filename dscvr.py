import typing
import typing_extensions
import socket
import sys
import json


Host = typing_extensions.TypedDict("Host", {"name": str, "address": str, "ports": typing.List[int]})


def read_scan_ranges(range_arg: str) -> typing.List[typing.Tuple[int, int]]:
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
            end_port = int(ports_range[1]) + 1
        else:
            start_port = int(ports_range)
            end_port = start_port + 1
        result.append((start_port, end_port))
    return result


def start_scan(hosts: typing.List[Host], port_ranges: typing.List[typing.Tuple[int, int]]):
    for host in hosts:
        for ports_range in ports_ranges:
            for port in range(ports_range[0], ports_range[1]):
                scan_host_ports((host['address'], port))


def scan_host_ports(sock: typing.Tuple[str, int]):
    socket.setdefaulttimeout(100)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        result = s.connect_ex(sock)
        print("Port {} is {} for {}".format(sock[1], 'open' if result == 0 else 'closed', sock[0]))


if __name__ == '__main__':
    hosts_file_path = sys.argv[1]
    if len(sys.argv) > 2:
        ports_ranges = read_scan_ranges(sys.argv[2])

    with open(hosts_file_path, "r") as hosts_file:
        hosts = json.load(hosts_file)
        if 'ports_ranges' in locals():
            start_scan(hosts, ports_ranges)
