from typing import Callable, Iterable
from .core import ParaO
from .action import Act, RecursiveAction


class RunAction(RecursiveAction):
    func: Callable[[ParaO], None]  # TODO: add dynamic tasks

    def _func(self, depth: int, inner: Iterable[Act]): ...  # TODO


class Task(ParaO):
    @RecursiveAction
    def remove(self, depth: int, inner: Iterable[Act]):
        pass

    @RecursiveAction
    def status(self, depth: int, inner: Iterable[Act]):
        pass
