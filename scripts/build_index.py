"""Validate every item and generate data/ai-engineer.json, skill and step READMEs, and the root README."""
import json
import re
import sys
from collections import Counter
from pathlib import Path

from manifest import COMING_SOON, SKILLS, item_file, step_dir

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://hemanth9336.github.io/AI-Engineer/"
REPO = "https://github.com/Hemanth9336/AI-Engineer"
ICON = {"lesson": "📘", "task": "🛠️", "quiz": "❓", "scenario": "🎭", "challenge": "🏆"}
LABEL = {"lesson": "Lesson", "task": "Task", "quiz": "Quiz", "scenario": "Scenario", "challenge": "Challenge"}


def parse(path):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", path.read_text(), re.S)
    if not m:
        raise ValueError(f"{path}: missing front matter")
    meta = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip().strip('"')
    return meta, m.group(2)


def check_quiz(path, body, errors):
    blocks = re.split(r"^### Q\d+\.", body, flags=re.M)[1:]
    if not blocks:
        errors.append(f"{path}: no questions")
    for i, block in enumerate(blocks, 1):
        if re.findall(r"^- ([A-D])\. ", block, re.M) != ["A", "B", "C", "D"]:
            errors.append(f"{path} Q{i}: options are not exactly A-D")
        if not re.search(r"\*\*Answer: ([A-D])\*\*", block):
            errors.append(f"{path} Q{i}: no answer")
    return len(blocks)


def build_skill(skill, errors):
    totals, questions, steps = Counter(), 0, []
    for step in skill["steps"]:
        folder = ROOT / skill["id"] / step_dir(step)
        items = []
        for i, (kind, title) in enumerate(step["items"], 1):
            path = folder / item_file(i, title)
            meta, body = parse(path)
            if meta.get("type") != kind or meta.get("title") != title.replace('"', "'"):
                errors.append(f"{path}: front matter mismatch {meta}")
            if body.strip() == "TODO" or len(body) < 300:
                errors.append(f"{path}: body missing or too short")
            entry = {"type": kind, "title": title, "minutes": int(meta.get("minutes", 3)),
                     "path": f"{skill['id']}/{step_dir(step)}/{path.name}"}
            if kind in ("quiz", "scenario"):
                entry["questions"] = check_quiz(path, body, errors)
                questions += entry["questions"]
            totals[kind] += 1
            items.append(entry)
        c = Counter(k for k, _ in step["items"])
        steps.append({"n": step["n"], "dir": f"{skill['id']}/{step_dir(step)}", "phase": step["phase"],
                      "title": step["title"], "summary": step["summary"], "minutes": step["minutes"],
                      "counts": {"lessons": c["lesson"], "tasks": c["task"], "quizzes": c["quiz"] + c["scenario"],
                                 "challenges": c["challenge"]},
                      "items": items})
    stats = {"topics": len(steps), "tasks": totals["task"], "quizzes": totals["quiz"] + totals["scenario"],
             "challenges": totals["challenge"], "lessons": totals["lesson"], "questions": questions, "minutes": sum(s["minutes"] for s in steps)}
    for k, v in skill.get("expected", {}).items():
        if stats[k] != v:
            errors.append(f"{skill['id']}: {k}={stats[k]} expected {v}")
    return {"id": skill["id"], "name": skill["name"], "icon": skill["icon"], "color": skill["color"],
            "tagline": skill["tagline"], "stats": stats,
            "phases": [{"id": a, "name": b, "blurb": c} for a, b, c in skill["phases"]], "steps": steps}


def write_step_readme(skill, step):
    phase = next(p for p in skill["phases"] if p["id"] == step["phase"])
    out = [f"# {step['n']:02d} - {step['title']}", "",
           f"> **{skill['icon']} {skill['name']}** · **Phase:** {phase['name']} · **Time:** ~{step['minutes']} min · "
           f"[Open in the interactive site]({SITE}#/{skill['id']}/{step['n']})", "",
           step["summary"], "", "| # | Type | Item | Time |", "|---|---|---|---|"]
    for i, it in enumerate(step["items"], 1):
        out.append(f"| {i} | {ICON[it['type']]} {LABEL[it['type']]} | [{it['title']}]({it['path'].split('/')[-1]}) | {it['minutes']}m |")
    steps = skill["steps"]
    idx = steps.index(step)
    nav = []
    if idx > 0:
        nav.append(f"⬅️ [{steps[idx-1]['n']:02d} {steps[idx-1]['title']}](../{steps[idx-1]['dir'].split('/')[1]}/)")
    nav.append(f"[🗺️ {skill['name']} roadmap](../README.md)")
    if idx < len(steps) - 1:
        nav.append(f"[{steps[idx+1]['n']:02d} {steps[idx+1]['title']}](../{steps[idx+1]['dir'].split('/')[1]}/) ➡️")
    out += ["", " · ".join(nav), ""]
    (ROOT / step["dir"] / "README.md").write_text("\n".join(out))


def skill_table(skill, link_prefix):
    out = []
    for pi, p in enumerate(skill["phases"], 1):
        out += [f"### Phase {pi} · {p['name']}", "", f"_{p['blurb']}_", "",
                "| Step | Topic | Time | 🛠️ Tasks | ❓ Quizzes |", "|---|---|---|---|---|"]
        for st in skill["steps"]:
            if st["phase"] == p["id"]:
                c = st["counts"]
                tasks = f"{c['tasks']}" + (f" + 🏆 {c['challenges']}" if c["challenges"] else "")
                out.append(f"| {st['n']:02d} | [{st['title']}]({link_prefix}{st['dir'].split('/')[1]}/) | ~{st['minutes']}m | {tasks} | {c['quizzes']} |")
        out.append("")
    return out


def write_skill_readme(skill):
    s = skill["stats"]
    ch = f" · {s['challenges']} challenges" if s["challenges"] else ""
    out = [f"# {skill['icon']} {skill['name']}", "", skill["tagline"], "",
           f"**{s['topics']} topics · {s['tasks']} hands-on tasks · {s['quizzes']} quizzes{ch} · ~{s['minutes']} min**", "",
           f"[▶ Open the interactive {skill['name']} path]({SITE}#/{skill['id']}) · [Set up your practice machine](../setup/README.md)", "",
           "## Roadmap", ""] + skill_table(skill, "") + ["[⬅️ Back to AI Engineer](../README.md)", ""]
    (ROOT / skill["id"] / "README.md").write_text("\n".join(out))


def write_root_readme(data):
    total = Counter()
    for sk in data["skills"]:
        for k in ("topics", "tasks", "quizzes", "minutes"):
            total[k] += sk["stats"][k]
    out = ['<div align="center">', "", "# 🤖 AI Engineer", "",
           "### Work with real LLM APIs from a live machine — raw HTTP, official SDKs, embeddings, RAG pipelines, customer deployments and agent harnesses, graded when you press Submit.", "",
           f"**{len(data['skills'])} skill{'s' if len(data['skills']) > 1 else ''} live · {total['topics']} topics · {total['tasks']} hands-on tasks · {total['quizzes']} quizzes · ~{round(total['minutes']/60)} hours**", "",
           f"[![Open the interactive roadmap](https://img.shields.io/badge/Open-Interactive%20Roadmap-7c5cff?style=for-the-badge&logo=openai&logoColor=white)]({SITE})",
           f"![Tasks](https://img.shields.io/badge/hands--on%20tasks-{total['tasks']}-1f8f4e?style=for-the-badge)",
           f"![Quizzes](https://img.shields.io/badge/quizzes-{total['quizzes']}-6f42c1?style=for-the-badge)", "",
           "</div>", "",
           "## 🚀 How it works", "",
           f"1. **Open the [interactive website]({SITE})** - progress is saved in your browser, quizzes are graded instantly.",
           "2. **Set up a practice machine** with [`setup/`](setup/README.md) - one Ubuntu VM plus the lab's AI gateway, connected to a model provider you choose.",
           "3. **Go in order.** Read each lesson, do every task, then run its **Check your work** script - every line should show ✅ before you mark it complete.",
           "4. **Finish with the projects** - small, real AI tools that combine the whole skill.", "",
           "| Icon | Item | What you do |", "|---|---|---|",
           "| 📘 | Lesson | Learn one idea with real prompts, requests, and code |",
           "| 🛠️ | Task | Do it against a real model on your machine, then verify with the checker script |",
           "| ❓ | Quiz | Quick multiple-choice check with explanations |",
           "| 🎭 | Scenario | A realistic on-the-job AI decision to reason through |",
           "| 🏆 | Challenge | A bigger graded job with only the goal given - no step-by-step |", "",
           "## 🧭 Skills", "", "| Skill | Topics | Tasks | Quizzes | Time | Status |", "|---|---|---|---|---|---|"]
    for sk in data["skills"]:
        s = sk["stats"]
        out.append(f"| {sk['icon']} [{sk['name']}]({sk['id']}/README.md) | {s['topics']} | {s['tasks']} | {s['quizzes']} | ~{s['minutes']} min | ✅ Live |")
    for cs in data["coming_soon"]:
        out.append(f"| {cs['icon']} {cs['name']} | - | - | - | - | 🔜 Coming next |")
    out.append("")
    for sk in data["skills"]:
        out += [f"## {sk['icon']} {sk['name']}", "", sk["tagline"], "", "```mermaid", "flowchart LR"]
        for i, p in enumerate(sk["phases"]):
            nums = [st["n"] for st in sk["steps"] if st["phase"] == p["id"]]
            out.append(f'  P{i}["{i+1}. {p["name"]}<br/>Steps {nums[0]:02d}-{nums[-1]:02d}"]')
        out += ["  " + " --> ".join(f"P{i}" for i in range(len(sk["phases"]))), "```", ""]
        out += skill_table(sk, f"{sk['id']}/")
    out += ["## 📁 Repository layout", "", "```text", "AI-Engineer/",
            "├── index.html                 # the interactive website (GitHub Pages)",
            "├── assets/                    # site styles and scripts",
            "├── data/ai-engineer.json      # generated index used by the site",
            "├── setup/                     # practice machine and AI gateway setup",
            "├── ai-fundamentals/           # one folder per skill",
            "│   ├── README.md              # skill roadmap",
            "│   ├── 01-what-is-generative-ai/",
            "│   │   ├── README.md          # step overview",
            "│   │   ├── 01-generative-ai-versus-traditional-software.md",
            "│   │   └── ...",
            "│   └── ... one folder per step ...",
            "├── docs/CONTENT_GUIDE.md      # format contract for new content",
            "└── scripts/                   # manifest, scaffold, and build/validation", "```", "",
            "## ➕ Adding the next skill", "",
            "1. Add the skill (steps and items) to `scripts/manifest.py`.",
            "2. `python3 scripts/scaffold.py` creates every folder and file.",
            "3. Write the content following [`docs/CONTENT_GUIDE.md`](docs/CONTENT_GUIDE.md).",
            "4. `python3 scripts/build_index.py` validates everything and updates the site and READMEs.", "",
            "## 🛠️ Run the site locally", "", "```bash", "python3 scripts/build_index.py", "python3 -m http.server 8000   # open http://localhost:8000", "```", "",
            "---", "", '<div align="center">Built by <a href="https://github.com/Hemanth9336">Hemanth</a> · ⭐ Star the repo if it helps you on your AI engineering journey</div>', ""]
    (ROOT / "README.md").write_text("\n".join(out))


def main():
    errors = []
    data = {"title": "AI Engineer", "skills": [build_skill(s, errors) for s in SKILLS], "coming_soon": COMING_SOON}
    for sk in data["skills"]:
        write_skill_readme(sk)
        for st in sk["steps"]:
            write_step_readme(sk, st)
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data/ai-engineer.json").write_text(json.dumps(data, indent=1, ensure_ascii=False))
    write_root_readme(data)
    for sk in data["skills"]:
        print(sk["id"], json.dumps(sk["stats"]))
    if errors:
        print("\n".join(errors))
        sys.exit(1)


if __name__ == "__main__":
    main()
