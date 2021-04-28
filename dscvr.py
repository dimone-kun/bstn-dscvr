import typing
import socket
import sys


def scan_host_ports(sock: typing.Tuple[str, int]):
    socket.setdefaulttimeout(100)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        result = s.connect_ex(sock)
        if result == 0:
            print("Port {} is open for {}".format(sock[1], sock[0]))


if __name__ == '__main__':
    host_address = socket.gethostbyname(sys.argv[1])
    host_port = int(sys.argv[2])
    scan_host_ports((host_address, host_port))
    pass
