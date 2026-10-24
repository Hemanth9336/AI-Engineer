"""Single source of truth for every skill: phases, steps, and items (in order).

Item types: lesson, task, quiz, scenario, challenge. Scenarios count as quizzes in the stats;
challenges are graded like tasks but counted separately.
To add a new skill, write scripts/<skill>_skill.py with the same shape, append it to SKILLS and run scripts/scaffold.py.
"""
import re

from ai_fundamentals_skill import AI_FUNDAMENTALS
from rag_skill import RAG
from fde_skill import FDE
from harness_skill import HARNESS

L, T, Q, S = "lesson", "task", "quiz", "scenario"

SKILLS = [AI_FUNDAMENTALS, RAG, FDE, HARNESS]

# Shown on the home page as upcoming skills until their content is added to SKILLS.
COMING_SOON = []

WEIGHT = {L: 5, T: 8, Q: 3, S: 3, "challenge": 12}


def slugify(text):
    text = text.lower().replace("'", "").replace("/", " ")
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text[:60].rstrip("-")


def step_dir(step):
    return f"{step['n']:02d}-{step['slug']}"


def item_file(index, title):
    return f"{index:02d}-{slugify(title)}.md"


def item_minutes(step):
    """Split the step's minutes across its items by weight, keeping the exact total."""
    weights = [WEIGHT[k] for k, _ in step["items"]]
    total = sum(weights)
    mins = [max(1, round(step["minutes"] * w / total)) for w in weights]
    while sum(mins) > step["minutes"]:
        mins[mins.index(max(mins))] -= 1
    mins[-1] += step["minutes"] - sum(mins)
    return mins
