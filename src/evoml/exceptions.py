from enum import StrEnum


class ErrorCode(StrEnum):
    """Базовый класс для всех кодов ошибок библиотеки EvoML."""


class GeneTypeCodes(ErrorCode):
    """Коды ошибок для GeneTypeError."""

    INVALID_BOUNDS = "GENE_INVALID_BOUNDS"
    INVALID_OPTIONS = "GENE_INVALID_OPTIONS"
    INVALID_LENGTH = "GENE_INVALID_LENGTH"


class ConfigCodes(ErrorCode):
    """Коды ошибок для ConfigError."""

    MISSING_FIELD = "CONFIG_MISSING_FIELD"
    INVALID_VALUE = "CONFIG_INVALID_VALUE"


class EvaluationCodes(ErrorCode):
    """Коды ошибок для EvaluationError."""

    COMPUTE_FAILED = "EVAL_COMPUTE_FAILED"


class EvoMLError(Exception):
    """Базовый класс для всех исключений библиотеки EvoML.

    Args:
        code: код ошибки из соответствующего класса констант
        message: человекочитаемое сообщение об ошибке
    """

    def __init__(self, code: ErrorCode, message: str) -> None:
        self._code = code
        self._message = message
        super().__init__(message)

    @property
    def code(self) -> ErrorCode:
        """Код ошибки."""
        return self._code

    @property
    def message(self) -> str:
        """Человекочитаемое сообщение об ошибке."""
        return self._message


class GeneTypeError(EvoMLError):
    """Ошибки конфигурации и работы типов генов."""


class ConfigError(EvoMLError):
    """Некорректная конфигурация эволюционного алгоритма."""


class EvaluationError(EvoMLError):
    """Ошибка при вычислении фитнеса."""
