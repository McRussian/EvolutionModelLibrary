# EvoML — Спецификация языка

## Содержание

1. [Основные понятия](#основные-понятия)
2. [Структура файла](#структура-файла)
3. [Блок extensions](#блок-extensions)
4. [Директива import](#директива-import)
5. [Блок primitives](#блок-primitives)
6. [Объявление genome](#объявление-genome)
7. [Типы генов](#типы-генов)
8. [Объявление fitness](#объявление-fitness)
9. [Блок evolve](#блок-evolve) (init, selection, strategy, replacement, using, stop\_when, checkpoint, observe, runs, islands, restart, log)
10. [Встроенные алгоритмы](#встроенные-алгоритмы)
11. [Расширения](#расширения)
12. [Формальная грамматика](#формальная-грамматика)
13. [Полные примеры](#полные-примеры)

---

## Основные понятия

### Особь и популяция

**Особь (Individual)** — одно конкретное решение задачи. Например, в задаче коммивояжёра — конкретный порядок обхода городов. В символьной регрессии — конкретное математическое выражение.

**Геном (Genome)** — описание структуры особи: какие поля и какого типа. Геном — шаблон, не хранит значений.

**Популяция (Population)** — множество особей фиксированного размера. Алгоритм работает сразу со всей популяцией.

### Поколение и операторы

**Поколение (Generation)** — одна итерация алгоритма:
1. Оценить всех особей через фитнес-функцию
2. Отобрать родителей
3. Создать потомков через скрещивание и мутацию
4. Заменить популяцию потомками

**Операторы:**
- **Инициализация (init)** — создание случайной особи с нуля
- **Мутация (mutate)** — случайное изменение одной особи
- **Скрещивание (crossover)** — создание потомков из двух родителей
- **Отбор (selection)** — выбор родителей из популяции

### Фитнес

**Фитнес** — числовая оценка качества особи. Направление оптимизации:
- `minimize` — чем меньше, тем лучше (ошибка, расстояние, стоимость)
- `maximize` — чем больше, тем лучше (точность, прибыль)

### Разнообразие

**Разнообразие (Diversity)** — мера отличия особей друг от друга, от 0 до 1.
- Высокое (0.8–1.0) — популяция исследует широкое пространство
- Снижение — сходимость к хорошим решениям
- Резкое падение до нуля — **преждевременная сходимость**, алгоритм застрял

### Фронт Парето

При оптимизации нескольких критериев одновременно единственного лучшего решения обычно нет.

**Решение A доминирует B** — если A не хуже B по всем критериям и лучше хотя бы по одному.

**Фронт Парето** — множество недоминируемых решений: у каждого нельзя улучшить один критерий без ухудшения другого.

**Гиперобъём (Hypervolume)** — численная метрика качества фронта Парето. Чем больше, тем лучше и шире фронт. Нормирован от 0 до 1.

---

## Структура файла

Блоки в фиксированном порядке:

```
[extensions]      ← необязателен
[import ...]      ← один или несколько
[primitives ...]  ← необязателен, только для Tree-геномов
[genome ...]      ← один или несколько
[fitness ...]     ← один или несколько
[evolve ...]      ← ровно один
```

Комментарии — строки, начинающиеся с `//`.

---

## Блок extensions

Регистрирует кастомные типы, алгоритмы, операторы и наблюдатели из Python-модулей.
Первый блок в файле, если присутствует.

```
extensions {
    gene_types: my_genes.MatrixGene, my_genes.GraphGene
    algorithms: my_algo.CMA_ES
    operators:  my_ops.TwoOpt, my_ops.BlendCrossover
    observers:  my_obs.PlotObserver
}
```

Каждая запись — `module.ClassName`. Модуль ищется относительно директории `.evo` файла.
После регистрации имена доступны по всему файлу. Секции необязательны.

---

## Директива import

Импортирует Python-модуль для получения данных и ссылок на функции.

```
import data      // data.cities, data.primitives, ...
import fitness   // fitness.calc_distance, ...
```

Модули ищутся относительно директории `.evo` файла.

---

## Блок primitives

Описывает набор допустимых операций для построения деревьев выражений (`Tree`).
Нужен только при использовании `Tree`-геномов.

### Именованный блок

Используется когда примитивы нужны в нескольких геномах или список большой:

```
primitives Math {
    functions: +(a,b), *(a,b), -(a,b), sin(x), cos(x),
               safe_div(a,b) = my_funcs.safe_div
    terminals: x, y
    constants: Ephemeral(-5.0, 5.0), Fixed(0.0, 1.0, -1.0)
}
```

Ссылка из генома: `Tree(Math, max_depth=6)`

### Инлайн

Когда примитивы нужны только для одного поля:

```
genome Expression {
    tree: Tree(max_depth=6) {
        functions: +(a,b), *(a,b), sin(x)
        terminals: x, y
        constants: Ephemeral(-5.0, 5.0)
    }
}
```

> `List[Tree]` — только именованные примитивы (инлайн синтаксически недопустим).

### Секции

**`functions`** — внутренние узлы дерева. Арность определяется числом аргументов.
Встроенные операторы (`+`, `*`, `sin`, ...) реализованы в EvoML.
Кастомные — ссылка на Python-функцию через `=`:

```
functions: +(a,b), sin(x), my_func(a,b,c) = my_funcs.custom
```

**`terminals`** — листья-переменные. Значения передаются при вычислении:

```python
g.tree.evaluate(x=2.0, y=3.5)
```

**`constants`** — листья-числа, хранятся внутри особи:
- `Ephemeral(min, max)` — случайная константа, генерируется при создании особи, может изменяться мутацией
- `Fixed(v1, v2, ...)` — фиксированный набор, при init выбирается одно значение

---

## Объявление genome

Описывает структуру особи: набор именованных полей и их типы.

```
genome Route {
    path:  Permutation(data.cities)
    speed: Float(1.0, 10.0)
    mode:  Categorical(fast, safe)
}
```

### Переопределение операторов

```
genome Route {
    path: Permutation(data.cities)
        with mutate    = TwoOpt(attempts=5)
        with crossover = OrderCrossover()
        with init      = NearestNeighbor(data.cities)
}
```

### Кодирование представления

Опциональный модификатор, изменяющий внутреннее представление и поведение операторов.

```
genome Solution {
    x:    Int(0, 255)       with encoding = GrayCode()
    s:    Float(1e-6, 1e6)  with encoding = LogScale()
    cat:  Categorical(a,b,c) with encoding = OneHot()
}
```

| Кодировка | Применимо к | Эффект |
|-----------|-------------|--------|
| `GrayCode()` | Int, BitString | соседние значения отличаются на 1 бит — мутации плавнее |
| `LogScale()` | Float | мутация в лог-пространстве — равномерное исследование на несколько порядков |
| `Fp16()` / `Fp32()` | Float | пониженная точность, меньше памяти |
| `OneHot()` | Categorical | хранится как битовый вектор |

Кодирование — продвинутая возможность, для большинства задач не нужна.

### Несколько геномов

```
genome Weights      { values: List[Float(-1.0, 1.0)](len=16) }
genome Architecture { layers: Int(1, 5), size: Categorical(32, 64, 128) }
```

### Геном-лес

Список деревьев — `List[Tree]`:

```
primitives Math { ... }

// фиксированный лес — ровно 3 дерева
genome Ensemble {
    trees: List[Tree(Math, max_depth=5)](len=3)
}

// переменный лес — от 2 до 6 деревьев
genome RuleSet {
    trees: List[Tree(Math, max_depth=4)](min=2, max=6)
}
```

Каждое дерево в списке независимо — своя структура, свои константы.
При переменной длине мутация включает добавление и удаление деревьев.

---

## Типы генов

Тип гена определяет: допустимые значения, инициализацию, мутацию, скрещивание.

### Скалярные

---

**`Int(min, max)`** — целое число в `[min, max]`.

```
layers: Int(1, 10)
age:    Int(18, 65)
```

- *Init*: равномерно случайное в диапазоне
- *Mutate*: случайное смещение `±delta`, зажать в `[min, max]`
- *Crossover*: случайный выбор значения одного из родителей
- *Encoding*: `GrayCode()`, `Binary()`

---

**`Float(min, max)`** — вещественное число в `[min, max]`.

```
speed:       Float(0.1, 10.0)
temperature: Float(-273.15, 1000.0)
```

- *Init*: равномерно случайное
- *Mutate*: гауссовский шум `σ = strength × (max − min)`, зажать
- *Crossover*: BLX-α (арифметическое среднее с расширением) или случайный выбор родителя
- *Encoding*: `Fp16()`, `Fp32()`, `Fp64()` (умолчание), `LogScale()`

---

**`Bool()`** — `true` / `false`.

- *Mutate*: инверсия с вероятностью `p`
- *Crossover*: случайный выбор родителя

---

**`Categorical(a, b, ...)`** — одно из перечисленных значений.

```
mode:  Categorical(fast, safe, balanced)
color: Categorical(red, green, blue)
```

- *Mutate*: замена на случайное другое значение из набора
- *Crossover*: случайный выбор родителя
- *Encoding*: `Ordinal()` (умолчание), `OneHot()`

---

### Структурные

---

**`Permutation(items)`** — перестановка элементов списка. Каждый ровно один раз.

```
path:  Permutation(data.cities)
order: Permutation(data.tasks)
```

- *Init*: случайное перемешивание
- *Mutate*: случайный **swap** двух позиций
- *Crossover*: **OX** — отрезок от первого родителя, остальное в порядке второго
- Длина фиксирована: `len(items)`

---

**`BitString(length)`** — строка из `length` битов.

```
mask: BitString(32)
```

- *Init*: случайные биты
- *Mutate*: каждый бит инвертируется с вероятностью `1/length`
- *Crossover*: одноточечное или равномерное
- *Encoding*: `GrayCode()`

---

**`Tree(primitives, max_depth)`** — дерево выражений.

```
expr: Tree(Math, max_depth=6)
// или инлайн:
expr: Tree(max_depth=6) { functions: ..., terminals: ..., constants: ... }
```

- *Init*: `ramped` (умолчание), `grow`, `full`
  - `grow` — случайная глубина и форма
  - `full` — все листья строго на `max_depth`
  - `ramped` — половина `grow`, половина `full`, глубина от 2 до `max_depth`
- *Mutate*: случайное поддерево заменяется новым случайным
- *Crossover*: у обоих родителей выбирается случайное поддерево, они обмениваются

---

### Составные

---

**`List[T](len=N)`** — список фиксированной длины.

```
weights: List[Float(-1.0, 1.0)](len=10)
```

- Операторы применяются к каждому элементу независимо
- *Crossover*: одноточечное или равномерное по позициям

---

**`List[T](min=M, max=N)`** — список переменной длины.

```
layers: List[Float(-1.0, 1.0)](min=2, max=8)
```

- *Init*: случайная длина в `[M, N]`
- *Mutate*: изменение значений + добавление/удаление элементов
- *Crossover*: `SegmentCrossover()` (умолчание) — обмен сегментами разной длины

---

**`Tuple[T1, T2, ...]`** — фиксированный набор разнотипных элементов.

```
point: Tuple[Float(-10.0, 10.0), Float(-10.0, 10.0)]
```

- Операторы применяются к каждой позиции по её типу

---

## Объявление fitness

### Короткая форма

Когда функция сразу возвращает `float`:

```
fitness minimize distance(g: Route)    = fitness.calc_distance
fitness maximize accuracy(g: Automaton) = fitness.classify
```

- `minimize` / `maximize` — направление оптимизации
- `g: Route` — имя аргумента и тип генома
- `= module.function` — ссылка на Python-функцию

### Длинная форма — двухуровневая схема

Когда функция возвращает нечисловое значение, которое нужно отдельно оценить:

```
fitness minimize accuracy(g: Classifier) {
    compute:  fitness.classify     // геном → любое значение
    evaluate: fitness.score        // то значение → float
}
```

```
геном → compute(g) → любое значение → evaluate(value) → float → алгоритм
```

`compute` возвращает что угодно: float, строку, список, объект.
`evaluate` всегда возвращает `float`.
Если `evaluate` не указан — тождественное отображение (когда `compute` возвращает число).

```python
# compute: геном → любое значение
def classify(g):
    return g.tree.evaluate(features=test_data)  # возвращает метку класса

# evaluate: значение → float
def score(value) -> float:
    return accuracy(value, true_labels)
```

### Многокритериальная из одной функции

```
fitness (minimize, minimize) from fitness.calc(g: Route)
```

`fitness.calc` возвращает `tuple[float, float]`. Порядок соответствует порядку направлений.

### Несколько отдельных функций

```
fitness minimize cost(g: Plan)        = fitness.calc_cost
fitness minimize time(g: Plan)        = fitness.calc_time
fitness maximize reliability(g: Plan) = fitness.calc_reliability
```

### Недопустимые решения

`compute` возвращает `None` → особь недопустима, алгоритм обрабатывает отдельно.

---

## Блок evolve

Ровно один блок на файл.

```
evolve Route
    init:        Random(size=200)
    selection:   Tournament(k=5)
    strategy:    Generational(elitism=2)
    replacement: Worst()
    using        GA(crossover_rate=0.9, mutation_rate=0.1)
    stop_when    fitness < 100.0 or elapsed > 5m
    checkpoint   every 100 to "checkpoint.json"
    observe      every 50: print_stats
```

### init — инициализация популяции

```
init: Random(size=200)                              // случайная (умолчание)
init: Seeded(data.known_solution, size=200, noise=0.1)  // от известного решения
init: FromFile("checkpoint.json")                   // из файла
init: my_init.custom_generator(size=200)            // кастомная
```

### selection — стратегия отбора родителей

```
selection: Tournament(k=5)    // k случайных особей, побеждает лучшая
selection: Roulette()         // вероятность ∝ фитнесу
selection: Rank()             // вероятность ∝ рангу в популяции
selection: SUS()              // Stochastic Universal Sampling, равномерный вариант Roulette
```

`Tournament` — рекомендуется по умолчанию: прост, эффективен, не чувствителен к масштабу фитнеса.

### strategy — стратегия замены поколений

```
strategy: Generational(elitism=2)       // все потомки заменяют родителей, кроме N лучших
strategy: SteadyState(replace=5)        // каждое поколение заменяется только N особей
strategy: MuLambda(mu=50, lambda=200)   // (μ,λ) — потомки заменяют родителей полностью
strategy: MuPlusLambda(mu=50, lambda=200) // (μ+λ) — лучшие из родителей + потомков
```

### replacement — кого вытесняют потомки

```
replacement: Worst()          // вытесняет худшую особь
replacement: Random()         // вытесняет случайную
replacement: Tournament(k=3)  // потомок вытесняет проигравшего в турнире
```

### using — алгоритм

```
using GA(crossover_rate=0.9, mutation_rate=0.1)
using NSGA2(population=200)
using GP(max_depth=6)
```

`selection`, `strategy`, `replacement` — независимы от `using`. Это позволяет менять одно без другого, и особенно важно для островов.

### stop_when — условие остановки

```
stop_when fitness < 50.0
stop_when generations > 1000
stop_when elapsed > 10m
stop_when hypervolume > 0.95       // для многокритериальных задач
stop_when fitness < 50.0 or elapsed > 5m
```

Единицы времени: `s`, `m`, `h`.

### checkpoint — сохранение состояния

```
checkpoint every 100 to "checkpoint.json"
```

Сохраняет: популяцию, номер поколения, состояние ГСЧ.
Продолжение: `evo run experiment.evo --resume checkpoint.json`

### observe — наблюдение

```
observe every 50: print_stats
observe every 100: save_history
observe every 10: PlotObserver
```

| Наблюдатель | Вывод |
|-------------|-------|
| `print_stats` | поколение, лучший фитнес, средний фитнес, разнообразие |
| `print_best` | геном лучшей особи и её фитнес |
| `print_pareto` | фронт Парето (только для NSGA2) |
| `save_history` | статистика каждого наблюдаемого поколения в `history.csv` |

### runs — несколько независимых запусков

```
runs:        10
parallel:    true
select_best: by_fitness
```

N независимых запусков алгоритма, выбирается лучший результат. `parallel: true` — запуски параллельно.

### islands — модель островов

Несколько популяций эволюционируют независимо и периодически обмениваются особями.

```
// одинаковые острова
islands: 4 using GA(population=100)

// разные острова
islands {
    A: GA(population=100)                         // использует глобальные умолчания
    B: GA(population=100, mutation_rate=0.4)      // другая мутация
    C: GA(population=100)
           selection   = Roulette()               // переопределить только отбор
           replacement = Tournament(k=3)
}
```

Глобальные `selection`, `strategy`, `replacement` — умолчания для всех островов. Каждый остров может переопределить свои.

```
migration {
    every:    50          // мигрировать каждые N поколений
    size:     5           // число мигрирующих особей
    topology: ring        // ring / complete / random
    send:     best        // кто уходит: best / random
    replace:  worst       // кого вытесняют: worst / random
}
```

### restart — рестарт при застревании

```
restart_when  diversity < 0.05          // популяция сошлась
restart_when  no_improvement > 100      // N поколений без улучшения
max_restarts: 5
on_restart:   Reseed(keep_best=10)      // оставить 10 лучших, остальные случайные
```

### log — логирование и сохранение результата

```
log {
    level:  info           // debug / info / warning / error
    file:   "run.log"      // писать в файл (опционально)
    result: "result.json"  // сохранить финальный результат
    seed:   42             // фиксированный seed для воспроизводимости
}
```

Без блока `log` — консольный вывод, уровень `info`, без сохранения.

**Уровни:**

| Уровень | Что пишет |
|---------|-----------|
| `error` | только ошибки |
| `warning` | ошибки + предупреждения (низкое diversity, нарушения ограничений) |
| `info` | системные события + прогресс из `observe` (умолчание) |
| `debug` | всё: каждая оценка фитнеса, мутации, внутренние состояния |

Пример консольного вывода на уровне `info`:

```
[INFO]  Загружен геном Route: 3 поля
[INFO]  Популяция инициализирована: 200 особей
[INFO]  Запуск GA, max_generations=500, seed=42
[INFO]  Gen  50: best=1203.4  avg=1489.2  diversity=0.78
[WARN]  Diversity упала до 0.06 — риск преждевременной сходимости
[INFO]  Gen 347: best=98.3    avg=112.5   diversity=0.31
[INFO]  Остановка: fitness < 100.0
[INFO]  Завершено за 14.2s
```

**CLI-флаги переопределяют блок `log`:**

```bash
evo run experiment.evo --log-level debug
evo run experiment.evo --quiet              # только ошибки
evo run experiment.evo --output result.json
evo run experiment.evo --seed 42
```

**Формат result.json:**

```json
{
  "evo_file": "route.evo",
  "seed": 42,
  "generations": 347,
  "stop_reason": "fitness < 100.0",
  "elapsed": "14.2s",
  "best": {
    "fitness": 98.3,
    "genome": { "path": ["..."], "speed": 4.3 }
  },
  "history": [
    { "generation": 0,   "best": 1847.3, "avg": 2341.1, "diversity": 0.91 },
    { "generation": 50,  "best": 1203.4, "avg": 1489.2, "diversity": 0.78 }
  ]
}
```

`history` включается если задан `observe ... : save_history`.

---

## Встроенные алгоритмы

### GA — генетический алгоритм

```
using GA(crossover_rate=0.9, mutation_rate=0.1, population=100, generations=500)
```

| Параметр | По умолчанию | Описание |
|----------|--------------|----------|
| `population` | 100 | Размер популяции |
| `generations` | 500 | Максимум поколений |
| `crossover_rate` | 0.9 | Вероятность скрещивания |
| `mutation_rate` | 0.1 | Вероятность мутации особи |

### NSGA2 — многокритериальный ГА

```
using NSGA2(population=200, generations=300)
```

Ранжирует популяцию по уровням доминирования. Внутри уровня — по **crowding distance** (расстояние до соседей на фронте), что сохраняет разнообразие решений на фронте.

| Параметр | По умолчанию | Описание |
|----------|--------------|----------|
| `population` | 200 | Размер популяции |
| `generations` | 300 | Максимум поколений |
| `crowding_distance` | true | Учитывать расстояние между особями |

Результат: фронт Парето.

### GP — генетическое программирование

```
using GP(population=100, generations=1000, max_depth=6, init_method=ramped)
```

| Параметр | По умолчанию | Описание |
|----------|--------------|----------|
| `population` | 100 | Размер популяции |
| `generations` | 1000 | Максимум поколений |
| `max_depth` | 6 | Максимальная глубина дерева |
| `init_method` | `ramped` | `grow` / `full` / `ramped` |
| `crossover_rate` | 0.9 | Вероятность скрещивания |
| `mutation_rate` | 0.1 | Вероятность мутации |

---

## Расширения

### Кастомный тип гена

```python
from evoml import GeneType

class MatrixGene(GeneType):
    def __init__(self, rows: int, cols: int, value_range: tuple[float, float]):
        self.rows, self.cols = rows, cols
        self.lo, self.hi = value_range

    def init(self):
        return [[random.uniform(self.lo, self.hi) for _ in range(self.cols)]
                for _ in range(self.rows)]

    def mutate(self, value, strength: float):
        result = [row[:] for row in value]
        i, j = random.randrange(self.rows), random.randrange(self.cols)
        result[i][j] = max(self.lo, min(self.hi,
                           result[i][j] + random.gauss(0, strength)))
        return result

    def crossover(self, a, b) -> tuple:
        child1 = [a[i] if random.random() < 0.5 else b[i] for i in range(self.rows)]
        child2 = [b[i] if random.random() < 0.5 else a[i] for i in range(self.rows)]
        return child1, child2
```

```
extensions { gene_types: my_genes.MatrixGene }

genome Network {
    weights: MatrixGene(4, 4, value_range=(-1.0, 1.0))
}
```

### Кастомный оператор мутации

**Функция** — без параметров:
```python
def my_mutate(value, gene_type):
    ...
    return new_value
```
```
path: Permutation(data.cities) with mutate = my_ops.my_mutate
```

**Класс** — с параметрами:
```python
from evoml import MutationOperator

class TwoOpt(MutationOperator):
    def __init__(self, attempts: int = 10):
        self.attempts = attempts

    def mutate(self, value: list, gene_type) -> list:
        result = value[:]
        for _ in range(self.attempts):
            i, j = sorted(random.sample(range(len(result)), 2))
            result[i:j+1] = result[i:j+1][::-1]
        return result
```
```
extensions { operators: my_ops.TwoOpt }

genome Route {
    path: Permutation(data.cities) with mutate = TwoOpt(attempts=5)
}
```

### Кастомный оператор скрещивания

**Функция** — без параметров:
```python
def my_crossover(a, b) -> tuple:
    ...
    return child1, child2
```
```
x: Float(0.0, 1.0) with crossover = my_ops.my_crossover
```

**Класс** — с параметрами:
```python
from evoml import CrossoverOperator

class BlendCrossover(CrossoverOperator):
    def __init__(self, alpha: float = 0.5):
        self.alpha = alpha

    def crossover(self, a, b, gene_type) -> tuple:
        lo, hi = gene_type.min, gene_type.max
        child1 = max(lo, min(hi, self.alpha * a + (1 - self.alpha) * b))
        child2 = max(lo, min(hi, (1 - self.alpha) * a + self.alpha * b))
        return child1, child2
```
```
extensions { operators: my_ops.BlendCrossover }

genome Solution {
    x: Float(0.0, 1.0) with crossover = BlendCrossover(alpha=0.3)
}
```

Для дерева: `a`, `b` — корни деревьев; `gene_type` даёт `max_depth` и `primitives`.

### Кастомный алгоритм

```python
from evoml import EvolutionAlgorithm, EvolutionResult

class CMA_ES(EvolutionAlgorithm):
    def __init__(self, population: int = 100, sigma: float = 0.3):
        self.population_size = population
        self.sigma = sigma

    def run(self, genome_type, fitness_functions, stop_condition, observers) -> EvolutionResult:
        ...
```
```
extensions { algorithms: my_algo.CMA_ES }

evolve Network using CMA_ES(sigma=0.5)
```

### Кастомный наблюдатель

```python
from evoml import Observer, GenerationStats

class PlotObserver(Observer):
    def update(self, generation: int, stats: GenerationStats) -> None:
        # stats.best_fitness, stats.avg_fitness, stats.diversity
        # stats.population, stats.pareto_front (только NSGA2)
        ...
```
```
extensions { observers: my_obs.PlotObserver }

evolve Route
    observe every 10: PlotObserver
```

---

## Формальная грамматика

```ebnf
program          = extensions_block? import_stmt*
                   primitives_block* genome_decl+
                   fitness_decl+ evolve_block

// Расширения
extensions_block = "extensions" "{" ext_section+ "}"
ext_section      = ext_key ":" qualified_name ("," qualified_name)*
ext_key          = "gene_types" | "algorithms" | "operators" | "observers"
qualified_name   = NAME ("." NAME)+

// Импорты
import_stmt      = "import" NAME

// Примитивы (для Tree)
primitives_block = "primitives" NAME "{" prim_section+ "}"
prim_section     = prim_key ":" prim_item ("," prim_item)*
prim_key         = "functions" | "terminals" | "constants"
prim_item        = func_decl | NAME | const_decl
func_decl        = NAME "(" NAME ("," NAME)* ")" ("=" dotted_name)?
const_decl       = "Ephemeral" "(" FLOAT "," FLOAT ")"
                 | "Fixed" "(" FLOAT ("," FLOAT)* ")"

// Геном
genome_decl      = "genome" NAME "{" field_decl+ "}"
field_decl       = NAME ":" type_expr field_modifier*
field_modifier   = "with" modifier_key "=" type_expr
modifier_key     = "mutate" | "crossover" | "init" | "encoding"

// Типы
type_expr        = NAME "(" arg_list? ")"
                 | NAME "(" arg_list? ")" "{" prim_section+ "}"   // Tree inline
                 | "List" "[" type_expr "]" "(" list_params ")"
                 | "Tuple" "[" type_expr ("," type_expr)* "]"
list_params      = "len" "=" INT
                 | "min" "=" INT "," "max" "=" INT
arg_list         = arg ("," arg)*
arg              = (NAME "=")? value
value            = INT | FLOAT | STRING | NAME | dotted_name
dotted_name      = NAME ("." NAME)+

// Фитнес
fitness_decl     = "fitness" direction NAME "(" NAME ":" NAME ")" "=" dotted_name
                 | "fitness" direction NAME "(" NAME ":" NAME ")" "{" fitness_body "}"
                 | "fitness" "(" direction ("," direction)+ ")"
                   "from" dotted_name "(" NAME ":" NAME ")"
fitness_body     = "compute" ":" dotted_name ("evaluate" ":" dotted_name)?
direction        = "minimize" | "maximize"

// Запуск
evolve_block     = "evolve" NAME evolve_stmt+
evolve_stmt      = init_stmt | using_stmt | selection_stmt | strategy_stmt
                 | replacement_stmt | runs_stmt | islands_block
                 | migration_block | restart_stmt | stop_stmt
                 | checkpoint_stmt | observe_stmt | log_block

init_stmt        = "init" ":" type_expr
using_stmt       = "using" type_expr
selection_stmt   = "selection" ":" type_expr
strategy_stmt    = "strategy" ":" type_expr
replacement_stmt = "replacement" ":" type_expr
runs_stmt        = "runs" ":" INT
                   ("parallel" ":" BOOL)?
                   ("select_best" ":" NAME)?

islands_block    = "islands" ":" INT "using" type_expr
                 | "islands" "{" island_decl+ "}"
island_decl      = NAME ":" type_expr island_override*
island_override  = ("selection" | "strategy" | "replacement") "=" type_expr

migration_block  = "migration" "{" migration_opt+ "}"
migration_opt    = "every" ":" INT | "size" ":" INT
                 | "topology" ":" NAME | "send" ":" NAME | "replace" ":" NAME

restart_stmt     = "restart_when" restart_cond
                 | "max_restarts" ":" INT
                 | "on_restart" ":" type_expr
restart_cond     = "diversity" "<" FLOAT
                 | "no_improvement" ">" INT

log_block        = "log" "{" log_opt+ "}"
log_opt          = "level"  ":" log_level
                 | "file"   ":" STRING
                 | "result" ":" STRING
                 | "seed"   ":" INT
log_level        = "debug" | "info" | "warning" | "error"

stop_stmt        = "stop_when" stop_cond ("or" stop_cond)*
stop_cond        = "fitness" comparator FLOAT
                 | "generations" ">" INT
                 | "elapsed" ">" duration
                 | "hypervolume" comparator FLOAT
comparator       = "<" | "<=" | ">" | ">=" | "=="
duration         = INT ("s" | "m" | "h")

checkpoint_stmt  = "checkpoint" "every" INT "to" STRING
observe_stmt     = "observe" "every" INT ":" NAME

// Лексика
NAME             = [a-zA-Z_][a-zA-Z0-9_]*
INT              = [0-9]+
FLOAT            = [0-9]+ "." [0-9]+
STRING           = '"' [^"]* '"'
BOOL             = "true" | "false"
COMMENT          = "//" [^\n]*
```

---

## Полные примеры

### Задача коммивояжёра (TSP)

```
// tsp/tsp.evo
import data
import fitness

extensions {
    operators: tsp_ops.TwoOpt, tsp_ops.OrderCrossover
}

genome Route {
    path: Permutation(data.cities)
        with mutate    = TwoOpt(attempts=10)
        with crossover = OrderCrossover()
}

fitness minimize distance(g: Route) = fitness.total_distance

evolve Route
    init:      Random(size=300)
    selection: Tournament(k=5)
    strategy:  Generational(elitism=2)
    using      GA(crossover_rate=0.9, mutation_rate=0.2)
    stop_when  fitness < 500.0 or elapsed > 2m
    checkpoint every 200 to "tsp_checkpoint.json"
    observe    every 100: print_stats
```

```python
# tsp/data.py
cities = [(0, 0), (1, 3), (4, 2), (2, 5), (6, 1)]

# tsp/fitness.py
import math

def total_distance(g) -> float:
    p = g.path
    return sum(math.dist(p[i], p[(i+1) % len(p)]) for i in range(len(p)))
```

---

### Символьная регрессия (GP)

```
// regression/regression.evo
import data
import fitness

primitives Math {
    functions: +(a,b), *(a,b), -(a,b), sin(x), safe_div(a,b) = data.safe_div
    terminals: x
    constants: Ephemeral(-5.0, 5.0)
}

genome Expression {
    tree: Tree(Math, max_depth=7)
}

fitness minimize mse(g: Expression) = fitness.mean_squared_error

evolve Expression
    init:     Random(size=200)
    strategy: Generational(elitism=1)
    using     GP(crossover_rate=0.9, mutation_rate=0.1)
    stop_when fitness < 0.001 or elapsed > 5m
    observe   every 100: print_best
```

---

### Многокритериальная оптимизация (острова)

```
// delivery/delivery.evo
import data
import fitness

genome DeliveryPlan {
    route: Permutation(data.locations)
    speed: Float(30.0, 120.0)
    load:  Int(1, 10)
}

fitness minimize cost(g: DeliveryPlan)        = fitness.calc_cost
fitness minimize time(g: DeliveryPlan)        = fitness.calc_time
fitness maximize reliability(g: DeliveryPlan) = fitness.calc_reliability

evolve DeliveryPlan
    init:      Random(size=100)
    selection: Tournament(k=3)
    strategy:  Generational(elitism=2)

    islands {
        A: NSGA2(population=100)                       // базовый
        B: NSGA2(population=100)
               selection = Roulette()                  // другой отбор
        C: NSGA2(population=100)
               strategy  = SteadyState(replace=10)    // другая стратегия
    }

    migration { every: 50, size: 5, topology: ring, send: best, replace: worst }

    restart_when  no_improvement > 100
    max_restarts: 3
    on_restart:   Reseed(keep_best=10)

    stop_when  hypervolume > 0.90 or elapsed > 10m
    checkpoint every 100 to "delivery_checkpoint.json"
    observe    every 50: print_pareto
```

---

### GP с нечисловым выходом (двухуровневый фитнес)

```
// dfa/dfa.evo
import data
import fitness

primitives BoolLogic {
    functions: and(a,b), or(a,b), not(x), xor(a,b)
    terminals: p, q, r
}

genome Classifier {
    rule: Tree(BoolLogic, max_depth=5)
}

fitness maximize accuracy(g: Classifier) {
    compute:  fitness.classify     // геном → список предсказанных меток
    evaluate: fitness.score        // список меток → float (доля правильных)
}

evolve Classifier
    init:     Random(size=150)
    strategy: Generational(elitism=2)
    using     GP(crossover_rate=0.85, mutation_rate=0.15)
    stop_when fitness > 0.99 or elapsed > 3m
    observe   every 50: print_stats
```
