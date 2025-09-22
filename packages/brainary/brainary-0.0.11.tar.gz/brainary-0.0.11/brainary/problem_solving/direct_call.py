# Divergent Thinking
# Convergent Thinking
# Critical Thinking (Brainstorming, Validity Check, Critique, Aggregation)
# Triz-40 Principles 


from abc import ABCMeta, abstractmethod
from typing import Dict, List, Type

from brainary.llm.llm import LLM, AUX_MODEL
from brainary.problem_solving.base import ProblemSolving

    
class DirectLLMCall(ProblemSolving):
    NAME = "direct llm call"
    DESC = "Invoke LLMs directly without applying complex problem-solving strategies. This approach is best suited for simple, straightforward instructions or when no suitable strategy exists."
    
    def __init__(self, llm: LLM):
        super().__init__(llm)
    
    def solve(self, task: str):
        return self.llm.request(task)