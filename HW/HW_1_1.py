from ipaddress import ip_address
from subprocess import PIPE, call
from tabulate import tabulate


def host_ping(*hosts: str) -> str:
    """
    Функция проверки доступности сетевых узлов.
    :hosts iter: объект, содержащий хосты или ip-адреса в строковом формате, которые необходимо проверить. Должен содержать метод __iter__
    :return: результат проверки
    """
    out = {
        'Reachable': [],
        'Unreachable': [],
    }
    for host in hosts:
        try:
            resp = call(['ping', str(ip_address(host))], stdout=PIPE)
        except ValueError:
            resp = call(['ping', host], stdout=PIPE)

        if resp == 0:
            out['Reachable'].append(host)
        else:
            out['Unreachable'].append(host)
    return out


if __name__ == '__main__':
    hosts = ('wikipedia.org', 'gb.ru', 'google.com', '192.168.100.1', '192.168.00.10')
    result = host_ping(*hosts)
    print(tabulate(result, headers='keys'))
