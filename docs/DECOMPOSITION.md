# EvoML — Декомпозиция реализации

> Архитектура: [ARCHITECTURE.md](ARCHITECTURE.md) | Язык: [LANGUAGE.md](LANGUAGE.md)

Разработка ведётся поэтапно. Каждый этап заканчивается чем-то проверяемым.
Эксперименты — сквозные прогоны от начала до конца, маяки прогресса.

---

## Этап 0 — Инфраструктура

| Шаг | Содержимое | Проверка | Готово |
|-----|-----------|----------|--------|
| 0.1 | Иерархия исключений: `EvoMLError`, `GeneTypeError`, `ConfigError`, `EvaluationError` | импорт без ошибок | [x] |
| 0.2 | `ErrorCode` StrEnum; `GeneTypeCodes`, `ConfigCodes`, `EvaluationCodes` | коды уникальны, работают как строки | [x] |
| 0.3 | `common.py`: `DEFAULT_RNG` и общие утилиты | импорт без ошибок | [x] |

---

## Этап 1 — Типы генов

| Шаг | Содержимое | Проверка | Готово |
|-----|-----------|----------|--------|
| 1.1 | `GeneType[T]` ABC; `CrossoverStrategy` ABC и все реализации с подиерархиями | импорт без ошибок | [ ] |
| 1.2 | `PrimitiveGeneType`: `IntGene`, `FloatGene` | диапазон, мутация не выходит за границы | [ ] |
| 1.3 | `BoolGene`, `CategoricalGene` | flip-мутация, элемент из options | [ ] |
| 1.4 | `PermutationGene` | OX-crossover сохраняет все элементы без повторов | [ ] |
| 1.5 | `BitStringGene` | flip-мутация, длина не меняется | [ ] |
| 1.6 | `CompositeGeneType` ABC | импорт без ошибок | [ ] |
| 1.7 | `ListGene(inner, len=N)`, `TupleGene(types...)` | crossover, мутация на фиксированном контейнере | [ ] |
| 1.8 | `StructGene(fields: dict[str, GeneType])` | `init()` возвращает словарь нужной структуры | [ ] |

---

## Этап 2 — Геном и индивид

| Шаг | Содержимое | Проверка | Готово |
|-----|-----------|----------|--------|
| 2.1 | `Genome(values: dict)` — иммутабельный, `__getitem__` | создание, доступ по ключу | [ ] |
| 2.2 | `Individual(genome, fitness)` — иммутабельный | сравнение по fitness | [ ] |
| 2.3 | `Population` — коллекция особей + `best`, `avg`, `diversity` | статистика на синтетических данных | [ ] |

---

## Этап 3 — Стратегии

| Шаг | Содержимое | Проверка | Готово |
|-----|-----------|----------|--------|
| 3.1 | `SelectionOperator`: `TournamentSelection(k)`, `RouletteSelection` | лучшие выбираются чаще | [ ] |
| 3.2 | `MutationOperator`: `StandardMutation(rate)` | rate=0 → нет изменений | [ ] |
| 3.3 | `CrossoverOperator`: `StandardCrossover` | дети содержат гены родителей | [ ] |
| 3.4 | `StopCondition`: `MaxGenerations`, `FitnessThreshold`, `MaxTime`, `AnyOf`, `AllOf` | остановка в нужный момент | [ ] |
| 3.5 | `InitStrategy`: `Random(size)`, `Seeded(genome, noise)` | генерирует N валидных геномов | [ ] |
| 3.6 | `EvolutionStrategy`: `Generational(elitism)`, `SteadyState(replace)` | размер популяции сохраняется | [ ] |
| 3.7 | `ReplacementOperator`: `Worst`, `Random` | | [ ] |

---

## Этап 4 — Движок + Эксперимент 1

| Шаг | Содержимое | Проверка | Готово |
|-----|-----------|----------|--------|
| 4.1 | `FitnessFunction` ABC, `FitnessDirection` | | [ ] |
| 4.2 | `EvolutionConfig` dataclass | создание, все поля доступны | [ ] |
| 4.3 | `Observer` ABC; `ConsoleObserver`, `HistoryObserver` | вывод прогресса | [ ] |
| 4.4 | `EvolutionResult`, `EvolutionState` | | [ ] |
| 4.5 | `EvolutionEngine` ABC, `GenerationalEngine` | полный цикл без ошибок | [ ] |
| 4.6 | **Эксперимент 1** | minimize x²+y² через `List[Float(-5,5)](len=2)`, Python API; fitness сходится к 0 | [ ] |

---

## Этап 5 — TreeGene + Эксперимент 2

| Шаг | Содержимое | Проверка | Готово |
|-----|-----------|----------|--------|
| 5.1 | `Node` ABC: `evaluate(**kwargs)`, `depth`, `size`, `copy()` | | [ ] |
| 5.2 | `FunctionNode(func, arity, children)` | evaluate вычисляет значение | [ ] |
| 5.3 | `ConstantNode(value)`, `EphemeralConstant(lo, hi)` | | [ ] |
| 5.4 | `ArgumentNode(name)` | возвращает kwargs[name] | [ ] |
| 5.5 | `PrimitiveSet` — регистрирует функции, терминалы, константы | ошибка при неверной арности | [ ] |
| 5.6 | Генераторы деревьев: `grow`, `full`, `ramped_half_and_half` | max_depth соблюдается | [ ] |
| 5.7 | `TreeGene(pset, max_depth)` реализует `GeneType`; `SubtreeMutation`, `SubtreeCrossover` | глубина не превышает лимит | [ ] |
| 5.8 | **Эксперимент 2** | символьная регрессия sin(x)+x², Python API; MSE < 0.01 | [ ] |

---

## Этап 6 — Python API

| Шаг | Содержимое | Проверка | Готово |
|-----|-----------|----------|--------|
| 6.1 | Публичные экспорты в `evoml/__init__.py` | `from evoml import IntGene, FloatGene, TreeGene, ...` | [ ] |
| 6.2 | Кастомный ген через `GeneType` ABC | Эксперимент 1 с кастомным геном | [ ] |
| 6.3 | Кастомный оператор через `MutationOperator` / `CrossoverOperator` | подключается без изменений движка | [ ] |
| 6.4 | `CheckpointObserver`: сохранить/загрузить состояние | продолжение эволюции с сохранённой популяции | [ ] |

---

## Этап 7 — NSGA-II + Эксперимент 3

| Шаг | Содержимое | Проверка | Готово |
|-----|-----------|----------|--------|
| 7.1 | Pareto-доминирование | тест на готовых примерах | [ ] |
| 7.2 | Быстрая недоминирующая сортировка | фронты совпадают с ожидаемыми | [ ] |
| 7.3 | Crowding distance | крайние точки имеют ∞ | [ ] |
| 7.4 | `NSGAConfig`, `NSGAEngine` | популяция сохраняет размер | [ ] |
| 7.5 | **Эксперимент 3** | двукритериальная оптимизация; фронт Парето виден на графике | [ ] |

---

## Этап 8 — DSL-парсер

| Шаг | Содержимое | Проверка | Готово |
|-----|-----------|----------|--------|
| 8.1 | lark: `import` + `genome` | парсит `genome Route { path: Permutation(...) }` | [ ] |
| 8.2 | `primitives` блок | именованный + инлайн | [ ] |
| 8.3 | `fitness` блок (короткая + длинная форма) | | [ ] |
| 8.4 | `evolve` базовый: `using`, `stop_when`, `observe` | | [ ] |
| 8.5 | `evolve` полный: `init`, `selection`, `strategy`, `replacement` | | [ ] |
| 8.6 | `evolve` расширенный: `runs`, `islands`, `migration`, `restart`, `log` | | [ ] |
| 8.7 | Человекочитаемые ошибки (строка + колонка) | неверный файл → понятное сообщение | [ ] |
| 8.8 | Тест: все 4 примера из LANGUAGE.md парсятся без ошибок | | [ ] |

---

## Этап 9 — DSL-интерпретатор + Эксперимент 4

| Шаг | Содержимое | Проверка | Готово |
|-----|-----------|----------|--------|
| 9.1 | `import` resolver → Python-модуль | `import fitness` → `sys.modules["fitness"]` | [ ] |
| 9.2 | `genome` → `StructGene` | | [ ] |
| 9.3 | `primitives` → `PrimitiveSet` | | [ ] |
| 9.4 | `fitness` → адаптер `FitnessFunction` (оба уровня: compute + evaluate) | | [ ] |
| 9.5 | `evolve` → `EvolutionConfig` или подкласс | | [ ] |
| 9.6 | Запуск: интерпретатор → движок → `EvolutionResult` | | [ ] |
| 9.7 | **Эксперимент 4** | TSP через `route.evo`; `evo run` заменяет Python API | [ ] |

---

## Этап 10 — CLI + пакет

| Шаг | Содержимое | Проверка | Готово |
|-----|-----------|----------|--------|
| 10.1 | `pyproject.toml`, entry point `evo` | `pip install -e .` → `evo --help` | [ ] |
| 10.2 | `evo validate <file>` | OK или список ошибок | [ ] |
| 10.3 | `evo inspect <file>` | печатает разобранную структуру | [ ] |
| 10.4 | `evo run <file>` | запускает Эксперимент 4 | [ ] |
| 10.5 | Флаги: `--seed`, `--log-level`, `--output`, `--resume` | каждый работает изолированно | [ ] |

---

## Этап 11 — Острова и мультизапуск + Эксперимент 5

| Шаг | Содержимое | Проверка | Готово |
|-----|-----------|----------|--------|
| 11.1 | `MultiRunConfig` + `MultiRunEngine`: N независимых запусков | результат лучше одного запуска | [ ] |
| 11.2 | `parallel: true` — запуски через `multiprocessing` | ускорение на N ядрах | [ ] |
| 11.3 | `IslandConfig` + `IslandEngine` — изолированные популяции | каждый остров эволюционирует независимо | [ ] |
| 11.4 | Миграция: `every N`, `size M`, `topology ring/complete` | особи мигрируют корректно | [ ] |
| 11.5 | `restart_when diversity < X` / `no_improvement > N` | рестарт срабатывает, лучшие сохраняются | [ ] |
| 11.6 | **Эксперимент 5** | острова на TSP; результат лучше одноостровного запуска | [ ] |

---

## Этап 12 — Переменная длина, Forest, кодировки + Эксперимент 6

| Шаг | Содержимое | Проверка | Готово |
|-----|-----------|----------|--------|
| 12.1 | `ListGene(inner, min=M, max=N)` — мутация включает add/remove | длина в пределах [min, max] | [ ] |
| 12.2 | Forest genome: `List[Tree(pset, max_depth)](min=2, max=6)` | мутация случайного дерева + add/remove | [ ] |
| 12.3 | `GrayCode` encoding для `IntGene` | соседние значения → 1 бит разницы | [ ] |
| 12.4 | `LogScale` encoding для `FloatGene` | мутация равномерна в лог-пространстве | [ ] |
| 12.5 | `OneHot` encoding для `CategoricalGene` | хранится как битовый вектор | [ ] |
| 12.6 | **Эксперимент 6** | ensemble GP через Forest genome; качество лучше одного дерева | [ ] |
