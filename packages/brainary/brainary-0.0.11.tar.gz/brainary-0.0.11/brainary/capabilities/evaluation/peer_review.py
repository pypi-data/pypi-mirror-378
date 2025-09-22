# peer_review.py
from .evaluation_base import Evaluation

class PeerReview(Evaluation):
    NAME = "Peer Review"
    DESC = (
        "Simulate peer review to assess clarity, quality, and compliance with best practices. "
        "Use this in formal quality control, structured evaluation, or professional standards."
    )

    def evaluate(self, task: str, result: str):
        prompt = (
            "You are a peer reviewer. Evaluate the output for quality, clarity, and adherence to best practices.\n\n"
            f"## Task\n{task}\n\n"
            f"## Output\n{result}\n\n"
            "## Guidelines\n"
            "- Provide structured review feedback.\n"
            "- Highlight strengths and weaknesses.\n"
            "- Avoid unrelated commentary.\n\n"
            "## Output Constraints\n"
            "- Do not use '#' for headings, as it is reserved as a system markup tag.\n"
            "- Use numbered or bullet points.\n"
            "- Do not include explanations, comments, or extra content."
        )
        return self.llm.request([prompt]).strip()
