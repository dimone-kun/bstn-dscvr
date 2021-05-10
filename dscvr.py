import typing
import socket
import sys


def scan_host_ports(sock: typing.Tuple[str, int]):
    socket.setdefaulttimeout(100)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        result = s.connect_ex(sock)
        print("Port {} is {} for {}".format(sock[1], 'open' if result == 0 else 'closed', sock[0]))


if __name__ == '__main__':
    hosts_file_path = sys.argv[1]
    with open(hosts_file_path, "r") as hosts_file:
        hosts = json.load(hosts_file)
        for host in hosts:
            for port in host['ports']:
                scan_host_ports((host['address'], port))
