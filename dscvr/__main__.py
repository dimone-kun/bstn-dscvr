import typing
import ipaddress
import sys
import logging
import asyncio
import json
from dscvr import DiscoveryService as discovery_service


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


async def main():
    found_hosts = await discovery_service.scan_hosts(hosts, ports, int(sys.argv[3])) if len(sys.argv) > 3 else await discovery_service.scan_hosts(hosts, ports)
    diff = discovery_service.assert_hosts(found_hosts)
    print(json.dumps(diff, indent=2))


logging.basicConfig(format="%(name)s %(levelname)s %(asctime)s: %(message)s", level=logging.DEBUG)

hosts = read_hosts(sys.argv[1])
ports = read_scan_ranges(sys.argv[2])

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
