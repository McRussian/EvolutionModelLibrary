# Стратегии скрещивания — описание для DSL

> Архитектура стратегий: [ARCHITECTURE.md](../ARCHITECTURE.md)

Стратегии скрещивания указываются в блоке `evolve` через ключ `crossover`.

---

## Иерархия

```
CrossoverStrategy
├── UniformCrossover          — универсальный, работает с любым типом
├── NumericCrossover
│   ├── BlendCrossover
│   ├── ArithmeticCrossover
│   └── BitLevelCrossover
├── ContainerCrossoverStrategy
│   ├── NPointContainerCrossover
│   ├── ElementWiseCrossover
│   └── MultiLevelCrossover
└── TreeCrossover
    └── SubtreeCrossover
```

---

## Таблица DSL-имён

| Класс | DSL-имя | Параметры | Применимо для |
|---|---|---|---|
| `UniformCrossover` | `uniform` | — | любой тип |
| `BlendCrossover` | `blend` | `alpha` (0.0–1.0, по умолчанию 0.5) | `Float` |
| `ArithmeticCrossover` | `arithmetic` | — | `Int`, `Float` |
| `BitLevelCrossover` | `bitlevel` | `n_points` (по умолчанию 1) | `Int`, `Float` |
| `NPointContainerCrossover` | `npoint` | `n_points` (по умолчанию 1) | `List`, `Tuple` |
| `ElementWiseCrossover` | `elementwise` | — | `List`, `Tuple` |
| `MultiLevelCrossover` | `multilevel` | `container`, `gene` | `List`, `Tuple` |
| `SubtreeCrossover` | `subtree` | — | `Tree` |

---

## Примеры в DSL

```
# Blend-скрещивание с параметром
crossover: blend(alpha=0.3)

# По умолчанию для Float
crossover: blend

# N-точечный контейнерный кроссовер
crossover: npoint(n_points=2)

# Многоуровневый: контейнер + элемент
crossover: multilevel(container=npoint(2), gene=blend(0.5))

# Универсальный свап
crossover: uniform
```

---

## Умолчания по типу гена

| Тип гена | Стратегия по умолчанию |
|---|---|
| `Float` | `blend(alpha=0.5)` |
| `Int` | `uniform` |
| `Bool` | `uniform` |
| `Categorical` | `uniform` |
| `Permutation` | *(определяется отдельно)* |
| `BitString` | `npoint(n_points=1)` |
| `List` | `npoint(n_points=1)` |
| `Tuple` | `elementwise` |
| `Struct` | `elementwise` |
| `Tree` | `subtree` |
