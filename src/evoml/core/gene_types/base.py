from __future__ import annotations

import struct
from abc import ABC, abstractmethod
from random import Random
from typing import Any, Generic, TypeVar

from evoml.core.common import DEFAULT_RNG
from evoml.exceptions import GeneTypeCodes, GeneTypeError

T = TypeVar("T")
NumT = TypeVar("NumT", int, float)

_INT_BIT_WIDTH = 32
_FLOAT_BIT_WIDTH = 64


def _n_point_bit_crossover(
    a_bits: str,
    b_bits: str,
    n_points: int,
    rng: Random,
) -> tuple[str, str]:
    """Выполняет n-точечный кроссовер над битовыми строками одинаковой длины.

    Args:
        a_bits: битовая строка первого родителя
        b_bits: битовая строка второго родителя
        n_points: желаемое количество точек разбиения
        rng: генератор случайных чисел

    Returns:
        Пара битовых строк — потомки.
    """
    length = len(a_bits)
    actual_points = min(n_points, length - 1)
    points = [0] + sorted(rng.sample(range(1, length), actual_points)) + [length]

    child1, child2 = "", ""
    use_a = True
    for idx in range(len(points) - 1):
        start, end = points[idx], points[idx + 1]
        if use_a:
            child1 += a_bits[start:end]
            child2 += b_bits[start:end]
        else:
            child1 += b_bits[start:end]
            child2 += a_bits[start:end]
        use_a = not use_a
    return child1, child2


class CrossoverStrategy(ABC, Generic[T]):
    """Базовый абстрактный класс стратегий скрещивания.

    Стратегия реализует конкретный способ получения двух дочерних значений
    из двух родительских. Ортогональна типу гена.
    """

    @abstractmethod
    def crossover(
        self,
        a: T,
        b: T,
        gene_type: GeneType[T],
        rng: Random = DEFAULT_RNG,
    ) -> tuple[T, T]:
        """Скрещивает два значения гена.

        Args:
            a: первое родительское значение
            b: второе родительское значение
            gene_type: тип гена (используется стратегиями, которым нужен доступ к его параметрам)
            rng: генератор случайных чисел

        Returns:
            Пара дочерних значений.
        """


class NumericCrossover(CrossoverStrategy[NumT], ABC):
    """Базовый класс стратегий скрещивания для числовых типов (int, float)."""


class ContainerCrossoverStrategy(CrossoverStrategy[list[Any]], ABC):
    """Базовый класс стратегий скрещивания для контейнерных типов (List, Tuple)."""


class TreeCrossover(CrossoverStrategy[T], ABC):
    """Базовый класс стратегий скрещивания для деревьев (Tree)."""


class UniformCrossover(CrossoverStrategy[T]):
    """Равномерное скрещивание: с вероятностью 0.5 обменивает значения родителей.

    Универсальная стратегия — применима к любому типу.
    Для контейнеров и деревьев меняет местами всё значение целиком.
    """

    def crossover(
        self,
        a: T,
        b: T,
        gene_type: GeneType[T],
        rng: Random = DEFAULT_RNG,
    ) -> tuple[T, T]:
        """Скрещивает два значения с равновероятным обменом.

        Args:
            a: первое родительское значение
            b: второе родительское значение
            gene_type: тип гена (не используется)
            rng: генератор случайных чисел

        Returns:
            Либо (a, b), либо (b, a) с вероятностью 0.5 каждый.
        """
        if rng.random() < 0.5:
            return b, a
        return a, b


class BlendCrossover(NumericCrossover[float]):
    """Blend-скрещивание для вещественных генов.

    child1 = a * α + b * (1 - α)
    child2 = a * (1 - α) + b * α

    Args:
        alpha: коэффициент смешивания, от 0.0 до 1.0

    Raises:
        GeneTypeError: если alpha не в диапазоне [0.0, 1.0]
    """

    def __init__(self, alpha: float = 0.5) -> None:
        if not (0.0 <= alpha <= 1.0):
            raise GeneTypeError(
                GeneTypeCodes.INVALID_BOUNDS,
                f"alpha must be in [0.0, 1.0], got {alpha}",
            )
        self._alpha = alpha

    @property
    def alpha(self) -> float:
        """Коэффициент смешивания."""
        return self._alpha

    def crossover(
        self,
        a: float,
        b: float,
        gene_type: GeneType[float],
        rng: Random = DEFAULT_RNG,
    ) -> tuple[float, float]:
        """Скрещивает два значения через линейное смешивание.

        Args:
            a: первое родительское значение
            b: второе родительское значение
            gene_type: тип гена (не используется)
            rng: генератор случайных чисел (не используется)

        Returns:
            Пара значений — взаимное смешивание a и b.
        """
        child1 = a * self._alpha + b * (1.0 - self._alpha)
        child2 = a * (1.0 - self._alpha) + b * self._alpha
        return child1, child2


class ArithmeticCrossover(NumericCrossover[NumT]):
    """Арифметическое скрещивание: оба потомка получают среднее значение родителей.

    Для int результат усекается до целого.
    """

    def crossover(
        self,
        a: NumT,
        b: NumT,
        gene_type: GeneType[NumT],
        rng: Random = DEFAULT_RNG,
    ) -> tuple[NumT, NumT]:
        """Скрещивает два числа через среднее арифметическое.

        Args:
            a: первое родительское значение
            b: второе родительское значение
            gene_type: тип гена (не используется)
            rng: генератор случайных чисел (не используется)

        Returns:
            Пара одинаковых значений — среднее a и b.
        """
        avg: NumT = type(a)((a + b) / 2)
        return avg, avg


class BitLevelCrossover(NumericCrossover[NumT]):
    """N-точечный кроссовер на уровне битового представления числа.

    Для int используется 32-битное представление в дополнительном коде.
    Для float — 64-битное представление IEEE 754. Если кроссовер порождает
    специальное значение (NaN, Inf), оно заменяется средним родителей.

    Args:
        n_points: количество точек разбиения, >= 1

    Raises:
        GeneTypeError: если n_points < 1
    """

    def __init__(self, n_points: int = 1) -> None:
        if n_points < 1:
            raise GeneTypeError(
                GeneTypeCodes.INVALID_BOUNDS,
                f"n_points must be >= 1, got {n_points}",
            )
        self._n_points = n_points

    @property
    def n_points(self) -> int:
        """Количество точек разбиения."""
        return self._n_points

    def crossover(
        self,
        a: NumT,
        b: NumT,
        gene_type: GeneType[NumT],
        rng: Random = DEFAULT_RNG,
    ) -> tuple[NumT, NumT]:
        """Скрещивает два числа на уровне бит.

        Args:
            a: первое родительское значение
            b: второе родительское значение
            gene_type: тип гена (не используется)
            rng: генератор случайных чисел

        Returns:
            Пара дочерних значений.
        """
        if isinstance(a, float):
            return self._crossover_float(a, b, rng)  # type: ignore[arg-type, return-value]
        return self._crossover_int(int(a), int(b), rng)  # type: ignore[return-value]

    def _crossover_float(self, a: float, b: float, rng: Random) -> tuple[float, float]:
        """Кроссовер на уровне бит для float (IEEE 754, 64 бита)."""
        a_int = struct.unpack("Q", struct.pack("d", a))[0]
        b_int = struct.unpack("Q", struct.pack("d", b))[0]
        a_bits = format(a_int, f"0{_FLOAT_BIT_WIDTH}b")
        b_bits = format(b_int, f"0{_FLOAT_BIT_WIDTH}b")

        c1_bits, c2_bits = _n_point_bit_crossover(a_bits, b_bits, self._n_points, rng)
        child1 = struct.unpack("d", struct.pack("Q", int(c1_bits, 2)))[0]
        child2 = struct.unpack("d", struct.pack("Q", int(c2_bits, 2)))[0]

        avg = (a + b) / 2
        if not (child1 == child1) or not (-1e308 <= child1 <= 1e308):
            child1 = avg
        if not (child2 == child2) or not (-1e308 <= child2 <= 1e308):
            child2 = avg
        return child1, child2

    def _crossover_int(self, a: int, b: int, rng: Random) -> tuple[int, int]:
        """Кроссовер на уровне бит для int (32-битное дополнительное представление)."""
        a_unsigned = a & 0xFFFFFFFF
        b_unsigned = b & 0xFFFFFFFF
        a_bits = format(a_unsigned, f"0{_INT_BIT_WIDTH}b")
        b_bits = format(b_unsigned, f"0{_INT_BIT_WIDTH}b")

        c1_bits, c2_bits = _n_point_bit_crossover(a_bits, b_bits, self._n_points, rng)
        child1_unsigned = int(c1_bits, 2)
        child2_unsigned = int(c2_bits, 2)

        child1 = child1_unsigned if child1_unsigned < 2**31 else child1_unsigned - 2**32
        child2 = child2_unsigned if child2_unsigned < 2**31 else child2_unsigned - 2**32
        return child1, child2


class NPointContainerCrossover(ContainerCrossoverStrategy):
    """N-точечный кроссовер на уровне контейнера (списка).

    Делит оба списка на n+1 сегментов и чередует их между потомками.
    Длины списков должны совпадать.

    Args:
        n_points: количество точек разбиения, >= 1

    Raises:
        GeneTypeError: если n_points < 1
    """

    def __init__(self, n_points: int = 1) -> None:
        if n_points < 1:
            raise GeneTypeError(
                GeneTypeCodes.INVALID_BOUNDS,
                f"n_points must be >= 1, got {n_points}",
            )
        self._n_points = n_points

    @property
    def n_points(self) -> int:
        """Количество точек разбиения."""
        return self._n_points

    def crossover(
        self,
        a: list[Any],
        b: list[Any],
        gene_type: GeneType[list[Any]],
        rng: Random = DEFAULT_RNG,
    ) -> tuple[list[Any], list[Any]]:
        """Скрещивает два списка n-точечным кроссовером.

        Args:
            a: первый родительский список
            b: второй родительский список
            gene_type: тип гена (не используется)
            rng: генератор случайных чисел

        Returns:
            Пара дочерних списков той же длины.

        Raises:
            GeneTypeError: если длины списков не совпадают
        """
        if len(a) != len(b):
            raise GeneTypeError(
                GeneTypeCodes.INVALID_LENGTH,
                f"container lengths must match, got {len(a)} and {len(b)}",
            )
        if len(a) <= 1:
            return list(a), list(b)

        actual_points = min(self._n_points, len(a) - 1)
        points = [0] + sorted(rng.sample(range(1, len(a)), actual_points)) + [len(a)]

        child1: list[Any] = []
        child2: list[Any] = []
        use_a = True
        for idx in range(len(points) - 1):
            start, end = points[idx], points[idx + 1]
            if use_a:
                child1.extend(a[start:end])
                child2.extend(b[start:end])
            else:
                child1.extend(b[start:end])
                child2.extend(a[start:end])
            use_a = not use_a
        return child1, child2


class ElementWiseCrossover(ContainerCrossoverStrategy):
    """Попарное скрещивание элементов через inner-ген контейнера.

    Для каждой пары элементов (a[i], b[i]) вызывает crossover внутреннего гена.
    Требует, чтобы gene_type имел атрибут inner (ListGene).
    Длины списков должны совпадать.
    """

    def crossover(
        self,
        a: list[Any],
        b: list[Any],
        gene_type: GeneType[list[Any]],
        rng: Random = DEFAULT_RNG,
    ) -> tuple[list[Any], list[Any]]:
        """Скрещивает два списка поэлементно через inner-ген.

        Args:
            a: первый родительский список
            b: второй родительский список
            gene_type: тип гена — должен иметь атрибут inner (ListGene)
            rng: генератор случайных чисел

        Returns:
            Пара дочерних списков той же длины.

        Raises:
            GeneTypeError: если длины списков не совпадают
        """
        if len(a) != len(b):
            raise GeneTypeError(
                GeneTypeCodes.INVALID_LENGTH,
                f"container lengths must match, got {len(a)} and {len(b)}",
            )
        inner = gene_type.inner  # type: ignore[attr-defined]
        child1: list[Any] = []
        child2: list[Any] = []
        for a_val, b_val in zip(a, b):
            c1, c2 = inner.crossover(a_val, b_val, rng)
            child1.append(c1)
            child2.append(c2)
        return child1, child2


class MultiLevelCrossover(ContainerCrossoverStrategy):
    """Многоуровневый кроссовер: сначала container-level, затем gene-level.

    Сначала применяет стратегию контейнера (обмен сегментами),
    затем для каждой пары соответствующих элементов применяет стратегию элемента.

    Args:
        container_strategy: стратегия на уровне контейнера
        gene_strategy: стратегия на уровне отдельного элемента
    """

    def __init__(
        self,
        container_strategy: ContainerCrossoverStrategy,
        gene_strategy: CrossoverStrategy[Any],
    ) -> None:
        self._container_strategy = container_strategy
        self._gene_strategy = gene_strategy

    @property
    def container_strategy(self) -> ContainerCrossoverStrategy:
        """Стратегия на уровне контейнера."""
        return self._container_strategy

    @property
    def gene_strategy(self) -> CrossoverStrategy[Any]:
        """Стратегия на уровне элемента."""
        return self._gene_strategy

    def crossover(
        self,
        a: list[Any],
        b: list[Any],
        gene_type: GeneType[list[Any]],
        rng: Random = DEFAULT_RNG,
    ) -> tuple[list[Any], list[Any]]:
        """Скрещивает два списка на двух уровнях.

        Args:
            a: первый родительский список
            b: второй родительский список
            gene_type: тип гена
            rng: генератор случайных чисел

        Returns:
            Пара дочерних списков.
        """
        c1, c2 = self._container_strategy.crossover(a, b, gene_type, rng)
        result1: list[Any] = []
        result2: list[Any] = []
        for v1, v2 in zip(c1, c2):
            r1, r2 = self._gene_strategy.crossover(v1, v2, gene_type, rng)
            result1.append(r1)
            result2.append(r2)
        return result1, result2


class SubtreeCrossover(TreeCrossover[T]):
    """Скрещивание поддеревьями для TreeGene.

    Реализуется в шаге 5 при добавлении TreeGene и Node-иерархии.
    """

    def crossover(
        self,
        a: T,
        b: T,
        gene_type: GeneType[T],
        rng: Random = DEFAULT_RNG,
    ) -> tuple[T, T]:
        """Скрещивает два дерева обменом случайных поддеревьев.

        Args:
            a: первое родительское дерево
            b: второе родительское дерево
            gene_type: тип гена
            rng: генератор случайных чисел

        Raises:
            NotImplementedError: реализуется в шаге 5
        """
        raise NotImplementedError("SubtreeCrossover is implemented in step 5 with TreeGene")


class GeneType(ABC, Generic[T]):
    """Базовый абстрактный класс для всех типов генов.

    Определяет три операции: инициализация, мутация, скрещивание.
    Скрещивание делегируется стратегии, заданной при создании.

    Args:
        crossover_strategy: стратегия скрещивания
    """

    def __init__(self, crossover_strategy: CrossoverStrategy[T]) -> None:
        self._crossover_strategy = crossover_strategy

    @property
    def crossover_strategy(self) -> CrossoverStrategy[T]:
        """Стратегия скрещивания."""
        return self._crossover_strategy

    @abstractmethod
    def init(self, rng: Random = DEFAULT_RNG) -> T:
        """Генерирует начальное случайное значение гена.

        Args:
            rng: генератор случайных чисел

        Returns:
            Новое случайное значение.
        """

    @abstractmethod
    def mutate(self, value: T, rng: Random = DEFAULT_RNG) -> T:
        """Мутирует значение гена.

        Args:
            value: текущее значение
            rng: генератор случайных чисел

        Returns:
            Новое значение после мутации.
        """

    def crossover(self, a: T, b: T, rng: Random = DEFAULT_RNG) -> tuple[T, T]:
        """Скрещивает два значения гена через стратегию.

        Args:
            a: первое родительское значение
            b: второе родительское значение
            rng: генератор случайных чисел

        Returns:
            Пара дочерних значений.
        """
        return self._crossover_strategy.crossover(a, b, self, rng)


class PrimitiveGeneType(GeneType[T], ABC):
    """Базовый класс для примитивных типов генов (скалярные значения).

    Примитивный ген хранит одно скалярное значение: число, булево, категорию.
    """


class CompositeGeneType(GeneType[T], ABC):
    """Базовый класс для составных типов генов.

    Составной ген содержит другие GeneType как параметры и делегирует
    операции вложенным генам.
    """
