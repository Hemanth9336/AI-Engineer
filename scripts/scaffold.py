"""Create every skill/step folder and item file (front matter only) without overwriting content."""
from pathlib import Path

from manifest import SKILLS, item_file, item_minutes, step_dir

ROOT = Path(__file__).resolve().parent.parent


def main():
    created = 0
    for skill in SKILLS:
        for step in skill["steps"]:
            folder = ROOT / skill["id"] / step_dir(step)
            folder.mkdir(parents=True, exist_ok=True)
            for i, ((kind, title), mins) in enumerate(zip(step["items"], item_minutes(step)), 1):
                path = folder / item_file(i, title)
                if path.exists():
                    continue
                safe_title = title.replace('"', "'")
                path.write_text(f'---\ntype: {kind}\ntitle: "{safe_title}"\nminutes: {mins}\n---\n\nTODO\n')
                created += 1
    print(f"created {created} placeholder files")


if __name__ == "__main__":
    main()
