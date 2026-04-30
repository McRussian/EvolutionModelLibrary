# EvoML — Architecture

> Описание языка и грамматики: [LANGUAGE.md](LANGUAGE.md)

## Идея

EvoML — высокоуровневый DSL для эволюционных вычислений. Пользователь описывает структуру генома и правило оценки в `.evo` файле, запускает через CLI (`evo run`). Типы генов автоматически порождают операторы инициализации, мутации и скрещивания.

В отличие от существующих решений (DEAP, gplearn), библиотека не ограничена математическими выражениями. Особь может быть любой структурой: деревом, графом, вектором, автоматом.

---

## Целевые задачи

### Генетическое программирование (GP)
Эволюция программ в виде деревьев выражений.

```
Примитивы: +, *, sin, x, y, константы
Особь:     (* (+ x 2.5) (sin y))
Фитнес:    среднеквадратичная ошибка на обучающих данных
```

### Генетические алгоритмы (GA)
Оптимизация векторов параметров.

```
Особь:     [0.3, 1.7, -0.5, 2.1, ...]
Фитнес:    значение целевой функции
```

### Детерминированный конечный автомат (ДКА)
Эволюция автоматов для распознавания языков.

```
Примитивы: алфавит {a, b}, состояния, переходы
Особь:     q0 -a→ q1, q0 -b→ q2, q1 -a→ q1 (принимающее)
Фитнес:    доля правильно классифицированных строк
Мутация:   изменить переход, добавить/убрать состояние
```

### Грамматики (Grammatical Evolution)
Эволюция программ через BNF-грамматику. Хромосома — целочисленный вектор,
разворачивающийся в программу через правила вывода.

```
Грамматика:
  <expr> ::= <expr> + <expr>
           | <expr> * <expr>
           | sin(<expr>)
           | x
```

### Стратегии игровых ботов (Behavior Trees)
Эволюция деревьев поведения для игровых агентов.

```
Примитивы:
  Условия:  health < 0.3, enemy_visible, has_ammo
  Действия: attack, flee, reload, patrol
  Узлы:     Sequence, Selector, Decorator

Особь:
  Selector
  ├── Sequence [health < 0.3 → flee]
  ├── Sequence [enemy_visible AND has_ammo → attack]
  └── patrol
```

---

## Сравнение с существующими библиотеками

| | DEAP | gplearn | PyGAD | **EvoML** |
|---|---|---|---|---|
| GP | ✓ | только регрессия | — | ✓ |
| GA | ✓ | — | ✓ | ✓ |
| Произвольный генотип | сложно | нет | нет | ✓ |
| ДКА / грамматики / BT | нет | нет | нет | ✓ |
| API | сложный | простой | простой | простой |
| Расширяемость | средняя | низкая | низкая | высокая |

---

## Архитектура

### 1. Иерархия типов генов

Все типы генов наследуются от `GeneType[T]`. Скрещивание — подключаемая стратегия,
ортогональная самому типу.

```
GeneType[T]
├── PrimitiveGeneType[T]
│   ├── IntGene(lo, hi)
│   ├── FloatGene(lo, hi)
│   ├── BoolGene
│   ├── CategoricalGene(options)
│   ├── PermutationGene(items)
│   └── BitStringGene(length)
├── CompositeGeneType[T]          ← содержит другие GeneType как параметры
│   ├── ListGene(inner, len=N)    ← фиксированный вектор однотипных генов
│   ├── TupleGene(types...)       ← фиксированный вектор разнотипных генов
│   └── StructGene(fields: dict)  ← именованные поля; создаётся из блока genome
└── TreeGene(pset, max_depth)     ← рекурсивная структура
```

Интерфейс `GeneType[T]`:

```python
class GeneType(ABC):
    crossover_strategy: CrossoverStrategy

    def init(self) -> T: ...
    def mutate(self, value: T) -> T: ...
    def crossover(self, a: T, b: T) -> tuple[T, T]:
        return self.crossover_strategy.crossover(a, b, self)
```

#### Стратегии скрещивания

Скрещивание работает на двух уровнях: внутри значения гена (bit-level, blend)
и на уровне контейнера (обмен кусками). Уровни можно комбинировать.

```
CrossoverStrategy
├── BlendCrossover(alpha)           ← Float: a·α + b·(1-α)
├── ArithmeticCrossover             ← Int/Float: среднее
├── UniformCrossover                ← Bool, Categorical: каждый элемент независимо
├── BitLevelCrossover(n_points)     ← Int/Float: обмен битами внутри значения
├── ContainerCrossover(n_points)    ← List: обмен сегментами контейнера
├── ElementWiseCrossover            ← List: попарно через inner.crossover()
├── MultiLevelCrossover(            ← List: контейнер + элемент одновременно
│       container, gene)
└── SubtreeCrossover                ← Tree: обмен поддеревьями
```

Умолчания по типу:

| Тип гена | Стратегия по умолчанию |
|----------|----------------------|
| `FloatGene` | `BlendCrossover(alpha=0.5)` |
| `IntGene` | `UniformCrossover` |
| `BitStringGene` | `ContainerCrossover(n_points=1)` |
| `ListGene` | `ContainerCrossover(n_points=1)` |
| `StructGene` | `ElementWiseCrossover` (поле за полем) |
| `TreeGene` | `SubtreeCrossover` |

#### Мутация — два уровня

- `GeneType.mutate(value)` — **атомарная** логика: как именно мутирует конкретный ген
- `MutationOperator.mutate(genome, gene_type)` — **политика**: какие поля и с какой вероятностью

`StandardMutation(rate)` перебирает поля `StructGene` и с вероятностью `rate` вызывает
`field_type.mutate(value)` для каждого. Сам оператор не знает про Float или Tree.

---

### 2. Геном и индивид

`StructGene` — описание структуры (фабрика значений). `Genome` — типизированный контейнер
конкретных значений. `Individual` — `Genome` + `fitness`.

```python
@dataclass(frozen=True)
class Genome:
    values: dict[str, Any]

    def __getitem__(self, key: str) -> Any:
        return self.values[key]

@dataclass(frozen=True)
class Individual:
    genome: Genome
    fitness: float | tuple[float, ...] | None = None
    # None → индивид недопустим (compute вернул None)
```

`StructGene` создаёт `Genome` через `init()`, мутирует и скрещивает через делегирование
в дочерние `GeneType`. Отдельного класса `Genome` на уровне описания не нужно —
структура живёт в `StructGene`.

---

### 3. Стратегии

Каждый компонент — отдельный ABC. Движок знает только об интерфейсах.

| ABC | Ключевой метод | Встроенные реализации |
|-----|---------------|----------------------|
| `SelectionOperator` | `select(population, n) → list[Individual]` | Tournament, Roulette, Rank, SUS |
| `MutationOperator` | `mutate(genome, gene_type) → Genome` | StandardMutation(rate) |
| `CrossoverOperator` | `crossover(a, b, gene_type) → tuple[Genome, Genome]` | StandardCrossover |
| `StopCondition` | `should_stop(state) → bool` | MaxGenerations, FitnessThreshold, MaxTime, AnyOf, AllOf |
| `InitStrategy` | `generate(gene_type, size) → list[Genome]` | Random, Seeded, FromFile |
| `EvolutionStrategy` | `next_gen(population, offspring) → Population` | Generational, SteadyState, MuLambda, MuPlusLambda |
| `ReplacementOperator` | `replace(population, offspring) → Population` | Worst, Random, Tournament |

`StopCondition` поддерживает Composite-паттерн:

```
StopCondition
├── MaxGenerations(n)
├── FitnessThreshold(value)
├── MaxTime(seconds)
├── AnyOf(conditions...)
└── AllOf(conditions...)
```

---

### 4. EvolutionConfig и движок

Все компоненты собираются в `EvolutionConfig`, движок принимает его целиком.

```python
@dataclass
class EvolutionConfig:
    gene_type:   StructGene
    fitness:     FitnessFunction
    selection:   SelectionOperator
    mutation:    MutationOperator
    crossover:   CrossoverOperator
    init:        InitStrategy
    strategy:    EvolutionStrategy
    replacement: ReplacementOperator
    stop:        StopCondition
    observers:   list[Observer]
    log:         LogConfig | None = None
```

По мере роста конфиг и движок образуют параллельные иерархии:

```
EvolutionConfig                  EvolutionEngine (ABC)
├── IslandConfig                 ├── GenerationalEngine
├── MultiRunConfig               ├── IslandEngine
└── ...                          ├── MultiRunEngine
                                 └── ...
```

DSL-интерпретатор строит нужный конфиг из блока `evolve` и передаёт движку —
пользователь не выбирает тип движка явно.

---

### 5. FitnessFunction

Движок видит единственный метод `evaluate`. Двухуровневость (`compute → evaluate`) —
деталь реализации конкретного функтора; DSL-интерпретатор собирает адаптер, который
внутри цепочит оба вызова.

```python
class FitnessFunction(ABC):
    @property
    def direction(self) -> FitnessDirection | tuple[FitnessDirection, ...]: ...

    def evaluate(self, genome: Genome) -> float | tuple[float, ...] | None: ...
```

- `FitnessDirection.MINIMIZE / MAXIMIZE` — движок не инвертирует вручную
- `None` → особь недопустима, движок её отбрасывает
- `tuple[float, ...]` + `tuple[FitnessDirection, ...]` → многокритериальный режим, движок использует NSGA-II

---

### 6. Observer

```
Observer (ABC)  ─  update(state: EvolutionState) → None
├── ConsoleObserver
├── HistoryObserver
└── CheckpointObserver
```

`EvolutionState` содержит: поколение, популяцию, лучшую особь, elapsed time.
Движок вызывает всех наблюдателей в конце каждого поколения.

---

### 7. DSL-слой

```
.evo файл
    ↓
Parser (lark)       → AST
    ↓
Interpreter         → EvolutionConfig (или подкласс)
    ↓
EvolutionEngine.run(config)
    ↓
EvolutionResult
```

Интерпретатор разворачивает каждый блок:

| Блок `.evo` | Результат |
|------------|-----------|
| `import fitness` | `sys.modules["fitness"]` — Python-модуль рядом с файлом |
| `genome Route { ... }` | `StructGene(fields={...})` |
| `primitives Math { ... }` | `PrimitiveSet` |
| `fitness minimize f(g: Route) = ...` | адаптер `FitnessFunction` |
| `fitness ... { compute: ... evaluate: ... }` | адаптер с двумя уровнями |
| `evolve Route using GA(...)` | `EvolutionConfig` |
| `evolve ... islands { ... }` | `IslandConfig` |
| `evolve ... runs: N` | `MultiRunConfig` |

---

### 8. Расширения

Пользователь добавляет кастомные типы через наследование от нужного ABC:

```python
# Кастомный тип гена
class GraphGene(CompositeGeneType[Graph]):
    def init(self) -> Graph: ...
    def mutate(self, value: Graph) -> Graph: ...

# Кастомный оператор мутации
class AdaptiveMutation(MutationOperator):
    def mutate(self, genome: Genome, gene_type: StructGene) -> Genome: ...

# Кастомный алгоритм
class DifferentialEvolution(EvolutionEngine):
    def run(self, config: EvolutionConfig) -> EvolutionResult: ...
```

В `.evo` файле:

```
extensions { operators: my_ops.GraphGene, my_ops.AdaptiveMutation }
```

---

## Структура проекта

```
EvolutionModelLibrary/
│
├── src/
│   └── evoml/
│       ├── __init__.py
│       ├── core/
│       │   ├── gene_types/
│       │   │   ├── base.py          # GeneType ABC, CrossoverStrategy иерархия
│       │   │   ├── primitive.py     # Int, Float, Bool, Categorical, Permutation, BitString
│       │   │   ├── composite.py     # ListGene, TupleGene, StructGene
│       │   │   └── tree.py          # TreeGene, PrimitiveSet, Node иерархия
│       │   ├── individual.py        # Genome, Individual
│       │   ├── population.py        # Population
│       │   ├── fitness.py           # FitnessFunction ABC, FitnessDirection
│       │   ├── strategies/
│       │   │   ├── selection.py     # Tournament, Roulette, Rank, SUS
│       │   │   ├── mutation.py      # StandardMutation
│       │   │   ├── crossover.py     # StandardCrossover
│       │   │   ├── stop.py          # MaxGenerations, FitnessThreshold, MaxTime, AnyOf, AllOf
│       │   │   ├── init.py          # Random, Seeded, FromFile
│       │   │   ├── strategy.py      # Generational, SteadyState, MuLambda, MuPlusLambda
│       │   │   └── replacement.py   # Worst, Random, Tournament
│       │   ├── config.py            # EvolutionConfig, IslandConfig, MultiRunConfig
│       │   ├── engine.py            # EvolutionEngine ABC, GenerationalEngine, IslandEngine, MultiRunEngine
│       │   ├── observer.py          # Observer ABC, ConsoleObserver, HistoryObserver, CheckpointObserver
│       │   └── result.py            # EvolutionResult, EvolutionState
│       ├── dsl/
│       │   ├── grammar.lark         # lark-грамматика
│       │   ├── parser.py            # .evo → AST
│       │   └── interpreter.py       # AST → EvolutionConfig
│       └── cli/
│           └── main.py              # evo run / validate / inspect
│
├── tests/
│   ├── test_gene_types/
│   ├── test_strategies/
│   ├── test_engine/
│   ├── test_dsl/
│   └── test_cli/
│
├── examples/
│   ├── tsp/
│   ├── symbolic_regression/
│   ├── dfa_evolution/
│   └── pareto/
│
└── docs/
    ├── LANGUAGE.md
    └── ARCHITECTURE.md
```

### Граф зависимостей

```
cli
 ↑
dsl
 ↑
core/config, core/engine
 ↑
core/strategies, core/fitness, core/observer
 ↑
core/individual, core/population
 ↑
core/gene_types
```

Нижние слои не знают о верхних. `gene_types` — единственная зависимость, которая есть у всех.

---

## Декомпозиция реализации

> Подробный план по шагам: [DECOMPOSITION.md](DECOMPOSITION.md)

| Этап | Содержимое | Эксперимент |
|------|-----------|-------------|
| 1 | Типы генов: `GeneType` ABC, `CrossoverStrategy`, все примитивы, `ListGene`, `TupleGene`, `StructGene` | |
| 2 | `Genome`, `Individual`, `Population` | |
| 3 | Стратегии: Selection, Mutation, Crossover, Stop, Init, EvolutionStrategy, Replacement | |
| 4 | `FitnessFunction`, `EvolutionConfig`, `Observer`, `GenerationalEngine` | **1**: minimize x²+y² |
| 5 | `TreeGene`: Node-иерархия, `PrimitiveSet`, генераторы, SubtreeCrossover/Mutation | **2**: символьная регрессия |
| 6 | Python API: публичные экспорты, кастомные расширения, чекпоинты | |
| 7 | NSGA-II: `NSGAConfig`, `NSGAEngine`, Pareto, crowding distance | **3**: многокритериальная оптимизация |
| 8 | DSL-парсер: lark, все блоки, error reporting | |
| 9 | DSL-интерпретатор: import → StructGene → FitnessFunction → EvolutionConfig → run | **4**: TSP через .evo |
| 10 | CLI: `evo run/validate/inspect`, `pyproject.toml`, флаги | |
| 11 | Острова и мультизапуск: `IslandConfig/Engine`, `MultiRunConfig/Engine`, миграция, restart | **5**: острова на TSP |
| 12 | Переменная длина, Forest genome, кодировки (GrayCode, LogScale, OneHot) | **6**: ensemble GP |
