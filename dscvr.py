import typing
import typing_extensions
import socket
import sys
import json


Host = typing_extensions.TypedDict("Host", {"name": str, "address": str, "ports": typing.List[int]})


def scan_host_ports(sock: typing.Tuple[str, int]):
    socket.setdefaulttimeout(100)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        result = s.connect_ex(sock)
        print("Port {} is {} for {}".format(sock[1], 'open' if result == 0 else 'closed', sock[0]))


if __name__ == '__main__':
    hosts_file_path = sys.argv[1]
    with open(hosts_file_path, "r") as hosts_file:
        hosts = json.load(hosts_file)
        for host in hosts:  # type: Host
            for port in host['ports']:
                scan_host_ports((host['address'], port))
