from typing import Any, Iterable, Callable
import csv
from copy import deepcopy
import itertools
from collections import defaultdict
import os
import tabulate

class IterableGrouped:
  _iter: Iterable
  _group_result = None
  
  def __init__(self, iterable: Iterable):
    self._iter = iterable
  
  def mean(self, column: str):
    self._group()
    r = dict()
    for groupname, csvobj in self.get(column, float).items():
      r[groupname] = csvobj.query().mean(column)
    return r
  
  def get(self, column: str, dtype = str):
    self._group()
    return dict(map(lambda kv: (
        kv[0], CSVObject(list(map(
            lambda d: {column: dtype(d[column])}, 
            kv[1]
            )))
    ), self._group_result.items()))
  
  def _group(self):
    if self._group_result is not None: return
    self._group_result = defaultdict(list)
    for k, v in self._iter:
      self._group_result[k].extend(v)

class IterableMethods:
  _iter: Iterable
  def __init__(self, iterable: Iterable):
    self._iter = iterable
  
  def groupby(self, key: Callable[[dict[str, Any]], Any]) -> IterableGrouped:
    return IterableGrouped(itertools.groupby(self._iter, key))

  def groupbycolumn(self, column: str) -> IterableGrouped:
    return self.groupby(lambda d: d[column])
  
  def mean(self, column: str) -> float:
    r = list(map(lambda d: float(d[column]), self._iter))
    return sum(r) / len(r)


class CSVObject:
  _data: list[dict[str, Any]]
  _columns: tuple[str]

  def __init__(self, data: list[dict[str, Any]]) -> None:
    if not data:
      raise ValueError("No data")
    if not self._validate_keys(data):
      raise ValueError("Passed heterogenous data")
    self._data = data
    self._columns = tuple(data[0].keys() or None)

  @property
  def columns(self) -> tuple[str]:
    return self._columns

  @classmethod
  def read_csv(cls, path: str):
    l = []
    with open(path, "r", newline='') as csvfile:
      spamreader = csv.DictReader(csvfile)
      for row in spamreader:
          l += [row]
    return cls(l)

  @staticmethod
  def _validate_keys(data: list[dict[str, Any]]) -> bool:
    k = data[0].keys()
    for v in data[1:]:
      if v.keys() != k:
        return False
    return True

  def concat(self, another, copy = True, inplace = False):
    merged = self._concat(self._data, another._data, copy)
    if inplace:
      self._data = merged
    else:
      return CSVObject(merged)

  @staticmethod
  def _concat(
      data1: list[dict[str, Any]],
      data2: list[dict[str, Any]],
      copy) -> list[dict[str, Any]]:
    if copy:
      data1 = deepcopy(data1)
      data2 = deepcopy(data2)
    data1.extend(data2)
    return data1
  
  def __iter__(self):
    class Iterator:
      def __init__(self_it):
        self_it.iterable = iter(self._data)
      def __next__(self_it):
        return next(self_it.iterable)
    return Iterator()
  
  def query(self) -> IterableMethods:
    return IterableMethods(self)
  
  def to_csv(self, filename: str, overwrite = False):
    if os.path.exists(filename) and not overwrite:
      raise OSError("File exists")
    with open(filename, "w", newline='') as csvfile:
      writer = csv.DictWriter(csvfile, fieldnames=self._columns)
      writer.writeheader()
      writer.writerows(self._data)
  
  def __str__(self):
    return tabulate.tabulate(self._data, headers="keys")
  
  def __repr__(self):
    return self._data.__repr__()

