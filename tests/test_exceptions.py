import unittest

from evoml.exceptions import (
    ConfigCodes,
    ConfigError,
    ErrorCode,
    EvaluationCodes,
    EvaluationError,
    EvoMLError,
    GeneTypeCodes,
    GeneTypeError,
)


class TestExceptionHierarchy(unittest.TestCase):
    """Тесты иерархии исключений."""

    def test_gene_type_error_is_evoml_error(self) -> None:
        self.assertTrue(issubclass(GeneTypeError, EvoMLError))

    def test_config_error_is_evoml_error(self) -> None:
        self.assertTrue(issubclass(ConfigError, EvoMLError))

    def test_evaluation_error_is_evoml_error(self) -> None:
        self.assertTrue(issubclass(EvaluationError, EvoMLError))

    def test_evoml_error_is_exception(self) -> None:
        self.assertTrue(issubclass(EvoMLError, Exception))


class TestExceptionAttributes(unittest.TestCase):
    """Тесты атрибутов исключений."""

    def test_code_stored(self) -> None:
        error = GeneTypeError(GeneTypeCodes.INVALID_BOUNDS, "lo must be < hi")
        self.assertEqual(error.code, GeneTypeCodes.INVALID_BOUNDS)

    def test_message_stored(self) -> None:
        error = GeneTypeError(GeneTypeCodes.INVALID_BOUNDS, "lo must be < hi")
        self.assertEqual(error.message, "lo must be < hi")

    def test_message_in_str(self) -> None:
        error = GeneTypeError(GeneTypeCodes.INVALID_BOUNDS, "lo must be < hi")
        self.assertEqual(str(error), "lo must be < hi")

    def test_message_in_args(self) -> None:
        message = "lo must be < hi"
        error = GeneTypeError(GeneTypeCodes.INVALID_BOUNDS, message)
        self.assertEqual(error.args[0], message)


class TestExceptionCatching(unittest.TestCase):
    """Тесты перехвата исключений по иерархии."""

    def test_catch_specific(self) -> None:
        with self.assertRaises(GeneTypeError):
            raise GeneTypeError(GeneTypeCodes.INVALID_BOUNDS, "lo must be < hi")

    def test_catch_as_evoml_error(self) -> None:
        with self.assertRaises(EvoMLError):
            raise GeneTypeError(GeneTypeCodes.INVALID_BOUNDS, "lo must be < hi")

    def test_catch_as_exception(self) -> None:
        with self.assertRaises(Exception):
            raise GeneTypeError(GeneTypeCodes.INVALID_BOUNDS, "lo must be < hi")

    def test_not_caught_as_sibling(self) -> None:
        with self.assertRaises(GeneTypeError):
            try:
                raise GeneTypeError(GeneTypeCodes.INVALID_BOUNDS, "lo must be < hi")
            except ConfigError:
                pass

    def test_chained_exception(self) -> None:
        original = ValueError("raw error")
        try:
            raise GeneTypeError(GeneTypeCodes.INVALID_BOUNDS, "lo must be < hi") from original
        except GeneTypeError as err:
            self.assertIs(err.__cause__, original)

    def test_distinguish_by_code(self) -> None:
        errors = [
            GeneTypeError(GeneTypeCodes.INVALID_BOUNDS, "bounds error"),
            GeneTypeError(GeneTypeCodes.INVALID_OPTIONS, "options error"),
            GeneTypeError(GeneTypeCodes.INVALID_LENGTH, "length error"),
        ]
        codes = [err.code for err in errors]
        self.assertEqual(len(set(codes)), 3)


class TestErrorCodeTypes(unittest.TestCase):
    """Тесты типов кодов ошибок."""

    def test_gene_type_codes_are_error_code(self) -> None:
        self.assertIsInstance(GeneTypeCodes.INVALID_BOUNDS, ErrorCode)

    def test_config_codes_are_error_code(self) -> None:
        self.assertIsInstance(ConfigCodes.MISSING_FIELD, ErrorCode)

    def test_evaluation_codes_are_error_code(self) -> None:
        self.assertIsInstance(EvaluationCodes.COMPUTE_FAILED, ErrorCode)

    def test_code_is_string(self) -> None:
        self.assertIsInstance(GeneTypeCodes.INVALID_BOUNDS, str)

    def test_code_value_in_fstring(self) -> None:
        result = f"[{GeneTypeCodes.INVALID_BOUNDS}]"
        self.assertEqual(result, "[GENE_INVALID_BOUNDS]")

    def test_code_equals_string(self) -> None:
        self.assertEqual(GeneTypeCodes.INVALID_BOUNDS, "GENE_INVALID_BOUNDS")


class TestErrorCodes(unittest.TestCase):
    """Тесты уникальности и формата кодов ошибок."""

    def test_gene_type_codes_unique(self) -> None:
        codes = [
            GeneTypeCodes.INVALID_BOUNDS,
            GeneTypeCodes.INVALID_OPTIONS,
            GeneTypeCodes.INVALID_LENGTH,
        ]
        self.assertEqual(len(codes), len(set(codes)))

    def test_config_codes_unique(self) -> None:
        codes = [
            ConfigCodes.MISSING_FIELD,
            ConfigCodes.INVALID_VALUE,
        ]
        self.assertEqual(len(codes), len(set(codes)))

    def test_evaluation_codes_unique(self) -> None:
        codes = [EvaluationCodes.COMPUTE_FAILED]
        self.assertEqual(len(codes), len(set(codes)))

    def test_all_codes_unique_across_classes(self) -> None:
        all_codes = [
            GeneTypeCodes.INVALID_BOUNDS,
            GeneTypeCodes.INVALID_OPTIONS,
            GeneTypeCodes.INVALID_LENGTH,
            ConfigCodes.MISSING_FIELD,
            ConfigCodes.INVALID_VALUE,
            EvaluationCodes.COMPUTE_FAILED,
        ]
        self.assertEqual(len(all_codes), len(set(all_codes)))


if __name__ == "__main__":
    unittest.main()
