__author__ = "McRussian Andrey"
# -*- coding: utf8 -*-


class CommonException(Exception):
    _msg_error: str = None
    _code_error: int = None

    def __init__(self, code: int, error: str):
        self._code_error = code
        self._msg_error = error

    def code_error(self) -> int:
        return self._code_error

    def msg_error(self) -> str:
        return type(self).__name__ + ': ' + self._msg_error
