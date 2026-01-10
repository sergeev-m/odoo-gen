from dataclasses import dataclass
from typing import Generic, TypeVar


T = TypeVar("T")
E = TypeVar("E")


class Result(Generic[T, E]):
    pass


@dataclass(slots=True)
class Ok(Result[T, E]):
    value: T


@dataclass(slots=True)
class Err(Result[T, E]):
    error: E
