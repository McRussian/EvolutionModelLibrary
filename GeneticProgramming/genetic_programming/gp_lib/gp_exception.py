from Common import CommonException


class GPException(CommonException):
    def __init__(self, code: int, error: str):
        super().__init__(code, error)


class NodeException(GPException):
    def __init__(self, code: int, error: str):
        super().__init__(code, error)


class ListArgumentsException(GPException):
    def __init__(self, code: int, error: str):
        super().__init__(code, error)
