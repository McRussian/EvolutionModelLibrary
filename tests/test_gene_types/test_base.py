import unittest
from random import Random
from typing import Any

from evoml.core.common import DEFAULT_RNG
from evoml.core.gene_types.base import (
    ArithmeticCrossover,
    BitLevelCrossover,
    BlendCrossover,
    CompositeGeneType,
    ContainerCrossoverStrategy,
    CrossoverStrategy,
    ElementWiseCrossover,
    GeneType,
    MultiLevelCrossover,
    NPointContainerCrossover,
    NumericCrossover,
    PrimitiveGeneType,
    SubtreeCrossover,
    TreeCrossover,
    UniformCrossover,
)
from evoml.exceptions import GeneTypeError


# --- Заглушки для тестирования абстрактных классов ---

class _DummyCrossover(CrossoverStrategy[int]):
    def crossover(self, a: int, b: int, gene_type: GeneType[int], rng: Random = DEFAULT_RNG) -> tuple[int, int]:
        return a, b


class _DummyGeneType(PrimitiveGeneType[int]):
    def __init__(self) -> None:
        super().__init__(_DummyCrossover())

    def init(self, rng: Random = DEFAULT_RNG) -> int:
        return 0

    def mutate(self, value: int, rng: Random = DEFAULT_RNG) -> int:
        return value + 1


class _DummyInnerGeneType(PrimitiveGeneType[int]):
    def __init__(self) -> None:
        super().__init__(UniformCrossover())

    def init(self, rng: Random = DEFAULT_RNG) -> int:
        return 0

    def mutate(self, value: int, rng: Random = DEFAULT_RNG) -> int:
        return value


class _DummyListGeneType(CompositeGeneType[list[int]]):
    """Заглушка ListGene с атрибутом inner для ElementWiseCrossover."""

    def __init__(self) -> None:
        super().__init__(ElementWiseCrossover())
        self.inner = _DummyInnerGeneType()

    def init(self, rng: Random = DEFAULT_RNG) -> list[int]:
        return []

    def mutate(self, value: list[int], rng: Random = DEFAULT_RNG) -> list[int]:
        return value


# --- Тесты иерархии стратегий ---

class TestStrategyHierarchy(unittest.TestCase):
    """Тесты иерархии подклассов стратегий скрещивания."""

    def test_numeric_crossover_is_crossover_strategy(self) -> None:
        self.assertTrue(issubclass(NumericCrossover, CrossoverStrategy))

    def test_container_crossover_strategy_is_crossover_strategy(self) -> None:
        self.assertTrue(issubclass(ContainerCrossoverStrategy, CrossoverStrategy))

    def test_tree_crossover_is_crossover_strategy(self) -> None:
        self.assertTrue(issubclass(TreeCrossover, CrossoverStrategy))

    def test_blend_is_numeric(self) -> None:
        self.assertTrue(issubclass(BlendCrossover, NumericCrossover))

    def test_arithmetic_is_numeric(self) -> None:
        self.assertTrue(issubclass(ArithmeticCrossover, NumericCrossover))

    def test_bitlevel_is_numeric(self) -> None:
        self.assertTrue(issubclass(BitLevelCrossover, NumericCrossover))

    def test_npoint_is_container(self) -> None:
        self.assertTrue(issubclass(NPointContainerCrossover, ContainerCrossoverStrategy))

    def test_elementwise_is_container(self) -> None:
        self.assertTrue(issubclass(ElementWiseCrossover, ContainerCrossoverStrategy))

    def test_multilevel_is_container(self) -> None:
        self.assertTrue(issubclass(MultiLevelCrossover, ContainerCrossoverStrategy))

    def test_subtree_is_tree(self) -> None:
        self.assertTrue(issubclass(SubtreeCrossover, TreeCrossover))

    def test_uniform_is_crossover_strategy(self) -> None:
        self.assertTrue(issubclass(UniformCrossover, CrossoverStrategy))

    def test_uniform_is_not_numeric(self) -> None:
        self.assertFalse(issubclass(UniformCrossover, NumericCrossover))

    def test_uniform_is_not_container(self) -> None:
        self.assertFalse(issubclass(UniformCrossover, ContainerCrossoverStrategy))


# --- Тесты абстрактности классов ---

class TestAbstractClasses(unittest.TestCase):
    """Тесты абстрактности базовых классов."""

    def test_crossover_strategy_is_abstract(self) -> None:
        with self.assertRaises(TypeError):
            CrossoverStrategy()  # type: ignore[abstract]

    def test_numeric_crossover_is_abstract(self) -> None:
        with self.assertRaises(TypeError):
            NumericCrossover()  # type: ignore[abstract]

    def test_container_crossover_strategy_is_abstract(self) -> None:
        with self.assertRaises(TypeError):
            ContainerCrossoverStrategy()  # type: ignore[abstract]

    def test_tree_crossover_is_abstract(self) -> None:
        with self.assertRaises(TypeError):
            TreeCrossover()  # type: ignore[abstract]

    def test_gene_type_is_abstract(self) -> None:
        with self.assertRaises(TypeError):
            GeneType(_DummyCrossover())  # type: ignore[abstract]

    def test_primitive_gene_type_is_abstract(self) -> None:
        with self.assertRaises(TypeError):
            PrimitiveGeneType(_DummyCrossover())  # type: ignore[abstract]

    def test_composite_gene_type_is_abstract(self) -> None:
        with self.assertRaises(TypeError):
            CompositeGeneType(_DummyCrossover())  # type: ignore[abstract]


# --- Тесты GeneType ---

class TestGeneType(unittest.TestCase):
    """Тесты базового поведения GeneType."""

    def setUp(self) -> None:
        self._gene = _DummyGeneType()

    def test_crossover_strategy_stored(self) -> None:
        self.assertIsInstance(self._gene.crossover_strategy, _DummyCrossover)

    def test_crossover_delegates_to_strategy(self) -> None:
        result = self._gene.crossover(1, 2)
        self.assertEqual(result, (1, 2))

    def test_init_returns_value(self) -> None:
        self.assertEqual(self._gene.init(), 0)

    def test_mutate_returns_value(self) -> None:
        self.assertEqual(self._gene.mutate(5), 6)


# --- Тесты UniformCrossover ---

class TestUniformCrossover(unittest.TestCase):
    """Тесты равномерного скрещивания."""

    def test_returns_one_of_two_combinations(self) -> None:
        strategy: UniformCrossover[int] = UniformCrossover()
        result = strategy.crossover(1, 2, None, DEFAULT_RNG)  # type: ignore[arg-type]
        self.assertIn(result, [(1, 2), (2, 1)])

    def test_values_are_preserved(self) -> None:
        strategy: UniformCrossover[int] = UniformCrossover()
        c1, c2 = strategy.crossover(10, 20, None, DEFAULT_RNG)  # type: ignore[arg-type]
        self.assertEqual({c1, c2}, {10, 20})

    def test_seeded_rng_deterministic(self) -> None:
        strategy: UniformCrossover[str] = UniformCrossover()
        rng1 = Random(42)
        rng2 = Random(42)
        result1 = strategy.crossover("a", "b", None, rng1)  # type: ignore[arg-type]
        result2 = strategy.crossover("a", "b", None, rng2)  # type: ignore[arg-type]
        self.assertEqual(result1, result2)


# --- Тесты BlendCrossover ---

class TestBlendCrossover(unittest.TestCase):
    """Тесты Blend-скрещивания."""

    def test_alpha_05_symmetric(self) -> None:
        strategy = BlendCrossover(alpha=0.5)
        c1, c2 = strategy.crossover(0.0, 1.0, None, DEFAULT_RNG)  # type: ignore[arg-type]
        self.assertAlmostEqual(c1, 0.5)
        self.assertAlmostEqual(c2, 0.5)

    def test_alpha_1_returns_parents(self) -> None:
        strategy = BlendCrossover(alpha=1.0)
        c1, c2 = strategy.crossover(2.0, 8.0, None, DEFAULT_RNG)  # type: ignore[arg-type]
        self.assertAlmostEqual(c1, 2.0)
        self.assertAlmostEqual(c2, 8.0)

    def test_alpha_0_swaps_parents(self) -> None:
        strategy = BlendCrossover(alpha=0.0)
        c1, c2 = strategy.crossover(2.0, 8.0, None, DEFAULT_RNG)  # type: ignore[arg-type]
        self.assertAlmostEqual(c1, 8.0)
        self.assertAlmostEqual(c2, 2.0)

    def test_children_sum_equals_parents_sum(self) -> None:
        strategy = BlendCrossover(alpha=0.3)
        c1, c2 = strategy.crossover(3.0, 7.0, None, DEFAULT_RNG)  # type: ignore[arg-type]
        self.assertAlmostEqual(c1 + c2, 10.0)

    def test_alpha_stored(self) -> None:
        self.assertAlmostEqual(BlendCrossover(alpha=0.7).alpha, 0.7)

    def test_invalid_alpha_negative(self) -> None:
        with self.assertRaises(GeneTypeError):
            BlendCrossover(alpha=-0.1)

    def test_invalid_alpha_above_one(self) -> None:
        with self.assertRaises(GeneTypeError):
            BlendCrossover(alpha=1.1)


# --- Тесты ArithmeticCrossover ---

class TestArithmeticCrossover(unittest.TestCase):
    """Тесты арифметического скрещивания."""

    def test_float_average(self) -> None:
        strategy: ArithmeticCrossover[float] = ArithmeticCrossover()
        c1, c2 = strategy.crossover(2.0, 8.0, None, DEFAULT_RNG)  # type: ignore[arg-type]
        self.assertAlmostEqual(c1, 5.0)
        self.assertAlmostEqual(c2, 5.0)

    def test_int_average(self) -> None:
        strategy: ArithmeticCrossover[int] = ArithmeticCrossover()
        c1, c2 = strategy.crossover(2, 8, None, DEFAULT_RNG)  # type: ignore[arg-type]
        self.assertEqual(c1, 5)
        self.assertEqual(c2, 5)

    def test_both_children_equal(self) -> None:
        strategy: ArithmeticCrossover[float] = ArithmeticCrossover()
        c1, c2 = strategy.crossover(1.0, 9.0, None, DEFAULT_RNG)  # type: ignore[arg-type]
        self.assertEqual(c1, c2)

    def test_int_type_preserved(self) -> None:
        strategy: ArithmeticCrossover[int] = ArithmeticCrossover()
        c1, c2 = strategy.crossover(3, 7, None, DEFAULT_RNG)  # type: ignore[arg-type]
        self.assertIsInstance(c1, int)
        self.assertIsInstance(c2, int)


# --- Тесты BitLevelCrossover ---

class TestBitLevelCrossover(unittest.TestCase):
    """Тесты битового скрещивания."""

    def test_int_type_preserved(self) -> None:
        strategy: BitLevelCrossover[int] = BitLevelCrossover(n_points=1)
        c1, c2 = strategy.crossover(100, 200, None, DEFAULT_RNG)  # type: ignore[arg-type]
        self.assertIsInstance(c1, int)
        self.assertIsInstance(c2, int)

    def test_float_type_preserved(self) -> None:
        strategy: BitLevelCrossover[float] = BitLevelCrossover(n_points=1)
        c1, c2 = strategy.crossover(1.5, 2.5, None, DEFAULT_RNG)  # type: ignore[arg-type]
        self.assertIsInstance(c1, float)
        self.assertIsInstance(c2, float)

    def test_float_no_nan_or_inf(self) -> None:
        strategy: BitLevelCrossover[float] = BitLevelCrossover(n_points=8)
        rng = Random(42)
        for _ in range(100):
            c1, c2 = strategy.crossover(1.0, -1.0, None, rng)  # type: ignore[arg-type]
            self.assertFalse(c1 != c1, "child1 is NaN")
            self.assertFalse(c2 != c2, "child2 is NaN")
            self.assertTrue(-1e308 <= c1 <= 1e308, f"child1 out of range: {c1}")
            self.assertTrue(-1e308 <= c2 <= 1e308, f"child2 out of range: {c2}")

    def test_n_points_stored(self) -> None:
        self.assertEqual(BitLevelCrossover(n_points=3).n_points, 3)

    def test_identical_parents_identical_children(self) -> None:
        strategy: BitLevelCrossover[int] = BitLevelCrossover(n_points=1)
        c1, c2 = strategy.crossover(42, 42, None, DEFAULT_RNG)  # type: ignore[arg-type]
        self.assertEqual(c1, 42)
        self.assertEqual(c2, 42)

    def test_invalid_n_points_zero(self) -> None:
        with self.assertRaises(GeneTypeError):
            BitLevelCrossover(n_points=0)

    def test_invalid_n_points_negative(self) -> None:
        with self.assertRaises(GeneTypeError):
            BitLevelCrossover(n_points=-1)


# --- Тесты NPointContainerCrossover ---

class TestNPointContainerCrossover(unittest.TestCase):
    """Тесты n-точечного контейнерного скрещивания."""

    def test_children_correct_length(self) -> None:
        strategy = NPointContainerCrossover(n_points=1)
        c1, c2 = strategy.crossover([1, 2, 3, 4, 5], [6, 7, 8, 9, 10], None, DEFAULT_RNG)  # type: ignore[arg-type]
        self.assertEqual(len(c1), 5)
        self.assertEqual(len(c2), 5)

    def test_children_contain_only_parent_values(self) -> None:
        strategy = NPointContainerCrossover(n_points=2)
        a, b = [1, 2, 3, 4], [5, 6, 7, 8]
        c1, c2 = strategy.crossover(a, b, None, DEFAULT_RNG)  # type: ignore[arg-type]
        all_values = set(a) | set(b)
        for val in c1 + c2:
            self.assertIn(val, all_values)

    def test_single_element_no_crossover(self) -> None:
        strategy = NPointContainerCrossover(n_points=1)
        c1, c2 = strategy.crossover([1], [2], None, DEFAULT_RNG)  # type: ignore[arg-type]
        self.assertEqual(c1, [1])
        self.assertEqual(c2, [2])

    def test_n_points_stored(self) -> None:
        self.assertEqual(NPointContainerCrossover(n_points=3).n_points, 3)

    def test_mismatched_lengths_raises(self) -> None:
        strategy = NPointContainerCrossover(n_points=1)
        with self.assertRaises(GeneTypeError):
            strategy.crossover([1, 2], [1, 2, 3], None, DEFAULT_RNG)  # type: ignore[arg-type]

    def test_invalid_n_points_raises(self) -> None:
        with self.assertRaises(GeneTypeError):
            NPointContainerCrossover(n_points=0)


# --- Тесты ElementWiseCrossover ---

class TestElementWiseCrossover(unittest.TestCase):
    """Тесты поэлементного скрещивания."""

    def test_children_correct_length(self) -> None:
        gene_type = _DummyListGeneType()
        c1, c2 = ElementWiseCrossover().crossover([1, 2, 3], [4, 5, 6], gene_type)
        self.assertEqual(len(c1), 3)
        self.assertEqual(len(c2), 3)

    def test_values_from_parents(self) -> None:
        gene_type = _DummyListGeneType()
        c1, c2 = ElementWiseCrossover().crossover([10, 20], [30, 40], gene_type)
        all_values = {10, 20, 30, 40}
        for val in c1 + c2:
            self.assertIn(val, all_values)

    def test_mismatched_lengths_raises(self) -> None:
        gene_type = _DummyListGeneType()
        with self.assertRaises(GeneTypeError):
            ElementWiseCrossover().crossover([1, 2], [1, 2, 3], gene_type)


# --- Тесты MultiLevelCrossover ---

class TestMultiLevelCrossover(unittest.TestCase):
    """Тесты многоуровневого скрещивания."""

    def test_children_correct_length(self) -> None:
        strategy = MultiLevelCrossover(
            container_strategy=NPointContainerCrossover(n_points=1),
            gene_strategy=UniformCrossover(),
        )
        c1, c2 = strategy.crossover([1, 2, 3, 4], [5, 6, 7, 8], _DummyListGeneType())
        self.assertEqual(len(c1), 4)
        self.assertEqual(len(c2), 4)

    def test_strategy_properties(self) -> None:
        container = NPointContainerCrossover(n_points=1)
        gene = UniformCrossover()
        strategy = MultiLevelCrossover(container_strategy=container, gene_strategy=gene)
        self.assertIs(strategy.container_strategy, container)
        self.assertIs(strategy.gene_strategy, gene)


# --- Тесты SubtreeCrossover ---

class TestSubtreeCrossover(unittest.TestCase):
    """Тесты заглушки SubtreeCrossover."""

    def test_raises_not_implemented(self) -> None:
        with self.assertRaises(NotImplementedError):
            SubtreeCrossover().crossover(None, None, None, DEFAULT_RNG)  # type: ignore[arg-type]

    def test_is_tree_crossover(self) -> None:
        self.assertIsInstance(SubtreeCrossover(), TreeCrossover)


if __name__ == "__main__":
    unittest.main()
