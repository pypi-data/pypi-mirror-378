# critical_reflection.py
from .evaluation_base import Evaluation

class CriticalReflection(Evaluation):
    NAME = "Critical Reflection"
    DESC = (
        "Evaluate outputs by considering broader implications, consequences, or systemic impacts. "
        "Use this in ethical, strategic, or high-stakes decision-making contexts."
    )

    def evaluate(self, task: str, result: str):
        prompt = (
            "You are an evaluator performing critical reflection. Analyze the output for potential consequences, impacts, and broader implications.\n\n"
            f"## Task\n{task}\n\n"
            f"## Output\n{result}\n\n"
            "## Guidelines\n"
            "- Consider social, ethical, operational, and strategic implications.\n"
            "- Summarize key insights succinctly.\n"
            "- Avoid extraneous commentary.\n\n"
            "## Output Constraints\n"
            "- Do not use '#' for headings, as it is reserved as a system markup tag.\n"
            "- Use numbered or bullet points.\n"
            "- Do not include explanations, comments, or extra content."
        )
        return self.llm.request([prompt]).strip()
