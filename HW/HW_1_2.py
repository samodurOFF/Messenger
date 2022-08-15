from ipaddress import ip_address, IPv4Address
from tabulate import tabulate
from HW_1_1 import host_ping


def host_range_ping(ip: IPv4Address, quantity: int) -> callable:
    """
    Проверка ip-адресов
    :param ip: начальный ip-адрес
    :param quantity: количество ip-адресов от начального
    :return: функция host_ping
    """

    ip_tuple = (ip + i for i in range(quantity))

    return host_ping(*ip_tuple)


if __name__ == '__main__':
    initial_ip = ip_address('192.168.100.253')
    quantity = 5
    print(tabulate(host_range_ping(initial_ip, quantity), headers='keys'))
