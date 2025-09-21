# Stream4Py

[![PyPI - Version](https://img.shields.io/pypi/v/stream4py.svg)](https://pypi.org/project/stream4py)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/stream4py.svg)](https://pypi.org/project/stream4py)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/FlavioAmurrioCS/stream4py/main.svg)](https://results.pre-commit.ci/latest/github/FlavioAmurrioCS/stream4py/main)


A Python library inspired by **Java Streams**, **Haskell lists**, and **Linux pipes**, providing a powerful, lazy-evaluated `Stream` class for functional-style data manipulation. Stream4Py makes it easy to work with iterables, files, subprocess output, and general data pipelines.

---

## Features

* Lazy and eager evaluation methods.
* Chainable operations like `map`, `filter`, `flat_map`, `unique`, `enumerate`, `flatten`, `sections`.
* File parsing and subprocess piping with `from_io` and `pipe`.
* Collection helpers like `to_list`, `to_dict`, `to_set`, and `cache`.
* Built-in itertools utilities (`islice`, `zip_longest`, `accumulate`, etc.).
* Inspired by Java Streams, Haskell functional programming, and Python itertools.

---

## Installation

Install via pip:

```bash
pip install stream4py
```

---

## Quick Start

```python
from stream4py import Stream

# Create a stream
s = Stream([1, 2, 3, 4, 5])

# Lazy operations
result = (
    s.filter(lambda x: x % 2 == 0)
     .map(lambda x: x * 10)
     .unique()
)

# Convert to list (triggers evaluation)
print(result.to_list())  # [20, 40]

# Stream lines from a file
lines = Stream.from_io(open("file.txt"))
lines.filter(lambda x: "error" in x).for_each(print)

# Subprocess streaming
Stream.subprocess_run(("seq", "100")).pipe(("grep", "1")).for_each(print)
```

---

## Quick Reference

| Method                                | Type  | Description                             | Example                                      |
| ------------------------------------- | ----- | --------------------------------------- | -------------------------------------------- |
| `map(func)`                           | Lazy  | Apply a function to each item           | `Stream([1,2,3]).map(lambda x: x*2)`         |
| `filter(predicate)`                   | Lazy  | Keep items satisfying a predicate       | `Stream([1,2,3]).filter(lambda x: x>1)`      |
| `filterfalse(predicate)`              | Lazy  | Keep items for which predicate is False | `Stream([1,2,3]).filterfalse(lambda x: x>1)` |
| `flat_map(func)`                      | Lazy  | Map then flatten iterables              | `Stream([1,2]).flat_map(lambda x: (x,x*10))` |
| `flatten()`                           | Lazy  | Flatten nested iterables                | `Stream([[1,2],[3]]).flatten()`              |
| `unique(key=None)`                    | Lazy  | Keep only unique items                  | `Stream([1,2,2]).unique()`                   |
| `type_is(cls)`                        | Lazy  | Keep items of a specific type           | `Stream([1,'a']).type_is(int)`               |
| `enumerate(start=0)`                  | Lazy  | Enumerate items                         | `Stream(['a','b']).enumerate(1)`             |
| `peek(func)`                          | Lazy  | Apply function without changing items   | `Stream([1,2]).peek(print)`                  |
| `islice(start, stop, step)`           | Lazy  | Slice like `itertools.islice`           | `Stream([1,2,3]).islice(1,3)`                |
| `batched(size)`                       | Lazy  | Yield items in batches                  | `Stream(range(5)).batched(2)`                |
| `drop(n)`                             | Lazy  | Drop first `n` items                    | `Stream([1,2,3]).drop(1)`                    |
| `take(n)`                             | Lazy  | Take first `n` items                    | `Stream([1,2,3]).take(2)`                    |
| `dropwhile(predicate)`                | Lazy  | Drop items while predicate is true      | `Stream([1,2,3]).dropwhile(lambda x: x<2)`   |
| `takewhile(predicate)`                | Lazy  | Take items while predicate is true      | `Stream([1,2,3]).takewhile(lambda x: x<3)`   |
| `reverse()`                           | Lazy  | Reverse the items                       | `Stream([1,2,3]).reverse()`                  |
| `zip(*iterables)`                     | Lazy  | Zip with other iterables                | `Stream([1,2]).zip(['a','b'])`               |
| `zip_longest(*iterables)`             | Lazy  | Zip with padding                        | `Stream([1]).zip_longest([2,3])`             |
| `accumulate(func=None, initial=None)` | Lazy  | Cumulative sums or function             | `Stream([1,2,3]).accumulate()`               |
| `subprocess_run(command)`             | Lazy  | Run a subprocess and stream output      | `Stream.subprocess_run(('ls',))`             |
| `pipe(command)`                       | Lazy  | Pipe stream to subprocess               | `Stream(['foo']).pipe(('grep','f'))`         |
| `sum(start=0)`                        | Eager | Sum all items                           | `Stream([1,2,3]).sum()`                      |
| `min(key=None, default=None)`         | Eager | Minimum value                           | `Stream([1,2,3]).min()`                      |
| `max(key=None, default=None)`         | Eager | Maximum value                           | `Stream([1,2,3]).max()`                      |
| `sorted(key=None, reverse=False)`     | Eager | Sort items                              | `Stream([3,1,2]).sorted()`                   |
| `first(default=None)`                 | Eager | First item                              | `Stream([1,2]).first()`                      |
| `find(func)`                          | Eager | Find first item matching function       | `Stream([1,2,3]).find(lambda x: x>1)`        |
| `group_by(key)`                       | Eager | Group items by key                      | `Stream([1,2,3,4]).group_by(lambda x: x%2)`  |
| `for_each(func)`                      | Eager | Apply function to all items             | `Stream([1,2]).for_each(print)`              |
| `cache()`                             | Eager | Cache stream items                      | `Stream(range(3)).cache()`                   |
| `to_list()`                           | Eager | Collect as list                         | `Stream([1,2]).to_list()`                    |
| `to_tuple()`                          | Eager | Collect as tuple                        | `Stream([1,2]).to_tuple()`                   |
| `to_set()`                            | Eager | Collect as set                          | `Stream([1,2]).to_set()`                     |
| `to_dict()`                           | Eager | Collect as dict (from tuples)           | `Stream([(1,'a')]).to_dict()`                |
| `collect(func)`                       | Eager | Apply function to iterable              | `Stream([1,2]).collect(sum)`                 |
| `from_io(io)`                         | Lazy  | Stream lines from file or binary IO     | `Stream.from_io(open('file.txt'))`           |
| `sections(predicate)`                 | Lazy  | Split into sections based on predicate  | `Stream([1,1,2]).sections(lambda x:x==2)`    |
| `range(start, stop, step=1)`          | Lazy  | Stream over a range                     | `Stream.range(1,5)`                          |

---

## Contributing

Contributions are welcome! Please open an issue or pull request with improvements or bug fixes.

---

## License

`stream4py` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
