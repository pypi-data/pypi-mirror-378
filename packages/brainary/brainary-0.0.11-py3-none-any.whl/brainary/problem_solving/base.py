# brainary/problem_solving/base.py
from abc import ABCMeta, abstractmethod
from typing import List

from brainary.llm.llm import LLM

class ProblemSolving(metaclass=ABCMeta):
    NAME = "Generic Problem Solving"
    DESC = "Abstract base class for all problem solving strategies. Should be extended by concrete implementations."

    def __init__(self, llm: LLM):
        self.llm = llm

    @abstractmethod
    def solve(self, task: str) -> str:
        """Execute the problem solving on a given task."""
        raise NotImplementedError
