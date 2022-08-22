import sys
import os
import unittest
from json import loads, dumps

from errors import IncorrectDataReceivedError

sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE, ENCODING
from common.utils import encode_message, decode_message


class Tests(unittest.TestCase):
    '''
    Тестовый класс
    '''

    test_dict_for_encode = {
        ACTION: PRESENCE,
        TIME: 111111.111111,
        USER: {
            ACCOUNT_NAME: 'test_test'
        }
    }
    test_dict_for_decode = {RESPONSE: 200}

    test_dict_for_decode_error = {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }

    def test_encode_message(self):
        """
        Тест корректности роботы функции кодирования сообщения
        """

        # вызов тестируемой функции, результаты будут сохранены в тестовом сокете
        result = dumps(self.test_dict_for_encode).encode(ENCODING)

        # Проверка корректности кодирования словаря.
        self.assertEqual(encode_message(self.test_dict_for_encode), result)

    def test_encode_message_error(self):
        """
        Тест корректности роботы функции кодирования на генерацию исключения, если на входе не словарь.
        """
        # дополнительно, проверяем генерацию исключения, при не словаре на входе.
        self.assertRaises(IncorrectDataReceivedError, encode_message, 1111)

    def test_decode_message(self):
        """
        Тест функции приёма сообщения
        """

        data = dumps(self.test_dict_for_decode).encode(ENCODING)

        # тест корректной расшифровки словаря
        self.assertEqual(decode_message(data), self.test_dict_for_decode)

    def test_decode_message_error(self):
        """
        Тест функции приёма сообщения
        """

        dats = dumps(self.test_dict_for_decode_error).encode(ENCODING)

        # тест корректной расшифровки ошибочного словаря
        self.assertEqual(decode_message(dats), self.test_dict_for_decode_error)


if __name__ == '__main__':
    unittest.main()
