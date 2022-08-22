from logging import getLogger

from common.variables import DEFAULT_PORT

logger = getLogger('server')


class Port:
    """
    Дескриптор для описания порта
    """

    def __set__(self, instance, value=DEFAULT_PORT):
        if not 1023 < value < 65536:
            logger.critical(
                f'Попытка запуска сервера с указанием неподходящего порта {value}. Допустимы адреса с 1024 до 65535.')
            exit(1)
        # Если порт прошёл проверку, добавляем его в список атрибутов экземпляра
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name
