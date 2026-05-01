import unittest
from random import Random

from evoml.core.gene_types.base import BlendCrossover, UniformCrossover
from evoml.core.gene_types.primitive import FloatGene, IntGene
from evoml.exceptions import GeneTypeCodes, GeneTypeError


class TestIntGeneCreation(unittest.TestCase):
    def test_valid_creation(self):
        gene = IntGene(0, 10)
        self.assertEqual(gene.lo, 0)
        self.assertEqual(gene.hi, 10)

    def test_negative_range(self):
        gene = IntGene(-10, -1)
        self.assertEqual(gene.lo, -10)
        self.assertEqual(gene.hi, -1)

    def test_default_crossover_is_uniform(self):
        gene = IntGene(0, 10)
        self.assertIsInstance(gene.crossover_strategy, UniformCrossover)

    def test_custom_crossover(self):
        strategy = BlendCrossover(alpha=0.3)
        gene = IntGene(0, 10, crossover_strategy=strategy)
        self.assertIs(gene.crossover_strategy, strategy)

    def test_lo_equals_hi_raises(self):
        with self.assertRaises(GeneTypeError) as context:
            IntGene(5, 5)
        self.assertEqual(context.exception.code, GeneTypeCodes.INVALID_BOUNDS)

    def test_lo_greater_than_hi_raises(self):
        with self.assertRaises(GeneTypeError) as context:
            IntGene(10, 0)
        self.assertEqual(context.exception.code, GeneTypeCodes.INVALID_BOUNDS)


class TestIntGeneInit(unittest.TestCase):
    def test_init_returns_int(self):
        gene = IntGene(0, 10)
        value = gene.init()
        self.assertIsInstance(value, int)

    def test_init_within_bounds(self):
        gene = IntGene(3, 7)
        rng = Random(42)
        for _ in range(100):
            value = gene.init(rng)
            self.assertGreaterEqual(value, 3)
            self.assertLessEqual(value, 7)

    def test_init_can_reach_bounds(self):
        gene = IntGene(0, 1)
        rng = Random(0)
        values = {gene.init(rng) for _ in range(200)}
        self.assertIn(0, values)
        self.assertIn(1, values)

    def test_init_uses_rng(self):
        gene = IntGene(0, 100)
        v1 = gene.init(Random(1))
        v2 = gene.init(Random(1))
        self.assertEqual(v1, v2)


class TestIntGeneMutate(unittest.TestCase):
    def test_mutate_returns_int(self):
        gene = IntGene(0, 10)
        result = gene.mutate(5)
        self.assertIsInstance(result, int)

    def test_mutate_within_bounds(self):
        gene = IntGene(3, 7)
        rng = Random(42)
        for _ in range(100):
            result = gene.mutate(5, rng)
            self.assertGreaterEqual(result, 3)
            self.assertLessEqual(result, 7)

    def test_mutate_ignores_input_value(self):
        gene = IntGene(0, 1)
        rng = Random(42)
        results_from_0 = [gene.mutate(0, rng) for _ in range(50)]
        rng2 = Random(42)
        results_from_1 = [gene.mutate(1, rng2) for _ in range(50)]
        self.assertEqual(results_from_0, results_from_1)

    def test_mutate_uses_rng(self):
        gene = IntGene(0, 100)
        v1 = gene.mutate(50, Random(7))
        v2 = gene.mutate(50, Random(7))
        self.assertEqual(v1, v2)


class TestIntGeneCrossover(unittest.TestCase):
    def test_crossover_returns_tuple_of_ints(self):
        gene = IntGene(0, 10)
        c1, c2 = gene.crossover(3, 7)
        self.assertIsInstance(c1, int)
        self.assertIsInstance(c2, int)

    def test_uniform_crossover_returns_parents(self):
        gene = IntGene(0, 10)
        rng = Random(0)
        results = set()
        for _ in range(50):
            c1, c2 = gene.crossover(3, 7, rng)
            results.add((c1, c2))
        self.assertIn((3, 7), results)
        self.assertIn((7, 3), results)


class TestFloatGeneCreation(unittest.TestCase):
    def test_valid_creation(self):
        gene = FloatGene(0.0, 1.0)
        self.assertAlmostEqual(gene.lo, 0.0)
        self.assertAlmostEqual(gene.hi, 1.0)
        self.assertAlmostEqual(gene.sigma_ratio, 0.1)

    def test_custom_sigma_ratio(self):
        gene = FloatGene(-5.0, 5.0, sigma_ratio=0.2)
        self.assertAlmostEqual(gene.sigma_ratio, 0.2)

    def test_default_crossover_is_blend(self):
        gene = FloatGene(0.0, 1.0)
        self.assertIsInstance(gene.crossover_strategy, BlendCrossover)

    def test_custom_crossover(self):
        strategy = UniformCrossover()
        gene = FloatGene(0.0, 1.0, crossover_strategy=strategy)
        self.assertIs(gene.crossover_strategy, strategy)

    def test_lo_equals_hi_raises(self):
        with self.assertRaises(GeneTypeError) as context:
            FloatGene(1.0, 1.0)
        self.assertEqual(context.exception.code, GeneTypeCodes.INVALID_BOUNDS)

    def test_lo_greater_than_hi_raises(self):
        with self.assertRaises(GeneTypeError) as context:
            FloatGene(5.0, 0.0)
        self.assertEqual(context.exception.code, GeneTypeCodes.INVALID_BOUNDS)

    def test_zero_sigma_ratio_raises(self):
        with self.assertRaises(GeneTypeError) as context:
            FloatGene(0.0, 1.0, sigma_ratio=0.0)
        self.assertEqual(context.exception.code, GeneTypeCodes.INVALID_BOUNDS)

    def test_negative_sigma_ratio_raises(self):
        with self.assertRaises(GeneTypeError) as context:
            FloatGene(0.0, 1.0, sigma_ratio=-0.1)
        self.assertEqual(context.exception.code, GeneTypeCodes.INVALID_BOUNDS)


class TestFloatGeneInit(unittest.TestCase):
    def test_init_returns_float(self):
        gene = FloatGene(0.0, 1.0)
        value = gene.init()
        self.assertIsInstance(value, float)

    def test_init_within_bounds(self):
        gene = FloatGene(-3.0, 3.0)
        rng = Random(42)
        for _ in range(100):
            value = gene.init(rng)
            self.assertGreaterEqual(value, -3.0)
            self.assertLessEqual(value, 3.0)

    def test_init_uses_rng(self):
        gene = FloatGene(0.0, 1.0)
        v1 = gene.init(Random(99))
        v2 = gene.init(Random(99))
        self.assertAlmostEqual(v1, v2)


class TestFloatGeneMutate(unittest.TestCase):
    def test_mutate_returns_float(self):
        gene = FloatGene(0.0, 1.0)
        result = gene.mutate(0.5)
        self.assertIsInstance(result, float)

    def test_mutate_within_bounds(self):
        gene = FloatGene(-5.0, 5.0, sigma_ratio=0.5)
        rng = Random(42)
        for _ in range(200):
            result = gene.mutate(0.0, rng)
            self.assertGreaterEqual(result, -5.0)
            self.assertLessEqual(result, 5.0)

    def test_mutate_clamps_at_lower_bound(self):
        gene = FloatGene(0.0, 1.0, sigma_ratio=10.0)
        rng = Random(42)
        results = [gene.mutate(0.0, rng) for _ in range(200)]
        self.assertTrue(all(r >= 0.0 for r in results))

    def test_mutate_clamps_at_upper_bound(self):
        gene = FloatGene(0.0, 1.0, sigma_ratio=10.0)
        rng = Random(42)
        results = [gene.mutate(1.0, rng) for _ in range(200)]
        self.assertTrue(all(r <= 1.0 for r in results))

    def test_mutate_uses_rng(self):
        gene = FloatGene(0.0, 10.0)
        v1 = gene.mutate(5.0, Random(3))
        v2 = gene.mutate(5.0, Random(3))
        self.assertAlmostEqual(v1, v2)

    def test_mutate_sigma_affects_spread(self):
        rng1 = Random(42)
        rng2 = Random(42)
        gene_small = FloatGene(0.0, 10.0, sigma_ratio=0.01)
        gene_large = FloatGene(0.0, 10.0, sigma_ratio=0.5)
        results_small = [abs(gene_small.mutate(5.0, rng1) - 5.0) for _ in range(100)]
        results_large = [abs(gene_large.mutate(5.0, rng2) - 5.0) for _ in range(100)]
        self.assertLess(sum(results_small), sum(results_large))


class TestFloatGeneCrossover(unittest.TestCase):
    def test_crossover_returns_tuple_of_floats(self):
        gene = FloatGene(0.0, 1.0)
        c1, c2 = gene.crossover(0.2, 0.8)
        self.assertIsInstance(c1, float)
        self.assertIsInstance(c2, float)

    def test_blend_crossover_default_alpha(self):
        gene = FloatGene(0.0, 1.0)
        c1, c2 = gene.crossover(0.0, 1.0)
        self.assertAlmostEqual(c1, 0.5)
        self.assertAlmostEqual(c2, 0.5)


if __name__ == "__main__":
    unittest.main()
