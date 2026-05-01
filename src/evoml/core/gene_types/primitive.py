from __future__ import annotations

from random import Random

from evoml.core.common import DEFAULT_RNG
from evoml.core.gene_types.base import (
    BlendCrossover,
    CrossoverStrategy,
    PrimitiveGeneType,
    UniformCrossover,
)
from evoml.exceptions import GeneTypeCodes, GeneTypeError


class IntGene(PrimitiveGeneType[int]):
    """Целочисленный ген с равномерным распределением в диапазоне [lo, hi].

    Args:
        lo: нижняя граница (включительно)
        hi: верхняя граница (включительно)
        crossover_strategy: стратегия скрещивания; по умолчанию UniformCrossover

    Raises:
        GeneTypeError: если lo >= hi
    """

    def __init__(
        self,
        lo: int,
        hi: int,
        crossover_strategy: CrossoverStrategy[int] | None = None,
    ) -> None:
        if lo >= hi:
            raise GeneTypeError(
                GeneTypeCodes.INVALID_BOUNDS,
                f"lo must be < hi, got lo={lo}, hi={hi}",
            )
        super().__init__(crossover_strategy if crossover_strategy is not None else UniformCrossover())
        self._lo = lo
        self._hi = hi

    @property
    def lo(self) -> int:
        """Нижняя граница диапазона."""
        return self._lo

    @property
    def hi(self) -> int:
        """Верхняя граница диапазона."""
        return self._hi

    def init(self, rng: Random = DEFAULT_RNG) -> int:
        """Генерирует случайное целое число из [lo, hi].

        Args:
            rng: генератор случайных чисел

        Returns:
            Случайное целое число из [lo, hi].
        """
        return rng.randint(self._lo, self._hi)

    def mutate(self, value: int, rng: Random = DEFAULT_RNG) -> int:
        """Заменяет значение новым случайным числом из [lo, hi].

        Args:
            value: текущее значение (не используется)
            rng: генератор случайных чисел

        Returns:
            Новое случайное целое число из [lo, hi].
        """
        return rng.randint(self._lo, self._hi)


class FloatGene(PrimitiveGeneType[float]):
    """Вещественный ген с гауссовой мутацией и зажимом в диапазон [lo, hi].

    Мутация добавляет гауссов шум с сигмой sigma_ratio * (hi - lo),
    результат зажимается в [lo, hi].

    Args:
        lo: нижняя граница (включительно)
        hi: верхняя граница (включительно)
        sigma_ratio: доля длины диапазона, используемая как сигма мутации
        crossover_strategy: стратегия скрещивания; по умолчанию BlendCrossover(alpha=0.5)

    Raises:
        GeneTypeError: если lo >= hi или sigma_ratio <= 0
    """

    def __init__(
        self,
        lo: float,
        hi: float,
        sigma_ratio: float = 0.1,
        crossover_strategy: CrossoverStrategy[float] | None = None,
    ) -> None:
        if lo >= hi:
            raise GeneTypeError(
                GeneTypeCodes.INVALID_BOUNDS,
                f"lo must be < hi, got lo={lo}, hi={hi}",
            )
        if sigma_ratio <= 0:
            raise GeneTypeError(
                GeneTypeCodes.INVALID_BOUNDS,
                f"sigma_ratio must be > 0, got {sigma_ratio}",
            )
        super().__init__(crossover_strategy if crossover_strategy is not None else BlendCrossover())
        self._lo = lo
        self._hi = hi
        self._sigma_ratio = sigma_ratio

    @property
    def lo(self) -> float:
        """Нижняя граница диапазона."""
        return self._lo

    @property
    def hi(self) -> float:
        """Верхняя граница диапазона."""
        return self._hi

    @property
    def sigma_ratio(self) -> float:
        """Доля длины диапазона, используемая как сигма мутации."""
        return self._sigma_ratio

    def init(self, rng: Random = DEFAULT_RNG) -> float:
        """Генерирует случайное вещественное число из [lo, hi].

        Args:
            rng: генератор случайных чисел

        Returns:
            Случайное вещественное число из [lo, hi].
        """
        return rng.uniform(self._lo, self._hi)

    def mutate(self, value: float, rng: Random = DEFAULT_RNG) -> float:
        """Мутирует значение гауссовым шумом с зажимом в [lo, hi].

        Args:
            value: текущее значение
            rng: генератор случайных чисел

        Returns:
            Новое значение после мутации, гарантированно в [lo, hi].
        """
        sigma = self._sigma_ratio * (self._hi - self._lo)
        new_value = rng.gauss(value, sigma)
        return max(self._lo, min(self._hi, new_value))
