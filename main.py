"""Lesson Plan Generator."""
import argparse
import json
from pathlib import Path

import llm

PHASES = [("Starter", 0.10), ("Teach", 0.25), ("Guided practice", 0.25),
          ("Independent task", 0.25), ("Plenary & exit ticket", 0.15)]
BLOOM = [("identify", "define"), ("explain", "demonstrate"), ("evaluate", "design")]


def timings(minutes):
    raw = [round(minutes * p) for _, p in PHASES]
    raw[-1] += minutes - sum(raw)
    return list(zip([n for n, _ in PHASES], raw))


def plan(lesson):
    topic, subs = lesson["topic"], lesson["subtopics"]
    objectives = [f"{BLOOM[0][0].capitalize()} the key terms in {topic.lower()}",
                  f"{BLOOM[1][0].capitalize()} how {subs[0].lower()} works using an example",
                  f"{BLOOM[2][1].capitalize()} a simple {subs[-1].lower()} for a real problem"]
    acts = {
        "Starter": f"Quick question on the board: 'Where have you seen {topic.lower()} in daily life?' Pairs share.",
        "Teach": f"Explain {', '.join(subs)} with a worked example and a diagram.",
        "Guided practice": f"Class works through an example of {subs[0].lower()} together; teacher checks with mini whiteboards.",
        "Independent task": f"Learners complete a short task applying {subs[-1].lower()}.",
        "Plenary & exit ticket": "Learners answer the exit-ticket questions; teacher collects them to plan the next lesson.",
    }
    ai = llm.complete(f"Suggest one hands-on activity (2 sentences) to teach {topic} to {lesson['class']}.")
    if ai:
        acts["Guided practice"] = ai.strip()
    return {
        **lesson, "objectives": objectives, "phases": [(n, m, acts[n]) for n, m in timings(lesson["minutes"])],
        "support": f"Provide a worked example and sentence starters for {subs[0].lower()}.",
        "stretch": f"Ask learners to compare two approaches to {subs[-1].lower()} and justify which is better.",
        "exit_ticket": [f"What is {subs[0].lower()}?", f"Give one real example of {topic.lower()}.",
                        "What is one thing you are still unsure about?"],
    }


def to_md(p):
    lines = [f"# {p['subject']}: {p['topic']}", "",
             f"**Class:** {p['class']}  ·  **Duration:** {p['minutes']} minutes  ·  **Week {p['week']}**", "",
             "## Objectives", "", "By the end of the lesson, learners will be able to:", ""]
    lines += [f"{i}. {o}" for i, o in enumerate(p["objectives"], 1)]
    lines += ["", "## Lesson sequence", "", "| Phase | Minutes | Activity |", "|---|---:|---|"]
    lines += [f"| {n} | {m} | {a} |" for n, m, a in p["phases"]]
    lines += ["", "## Differentiation", "", f"- Support: {p['support']}", f"- Stretch: {p['stretch']}",
              "", "## Resources", "", f"- {', '.join(p['resources'])}", "", "## Exit ticket", ""]
    lines += [f"- {q}" for q in p["exit_ticket"]]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", default="sample_scheme.json")
    ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()
    lessons = [plan(l) for l in json.loads(Path(a.input).read_text())]
    Path("output").mkdir(exist_ok=True)
    scheme = ["# Scheme of work", "", "| Week | Class | Subject | Topic | Minutes |", "|---|---|---|---|---:|"]
    for p in lessons:
        name = f"output/{p['class'].replace(' ', '')}_{p['topic'].lower().replace(' ', '_')}.md"
        Path(name).write_text(to_md(p))
        scheme.append(f"| {p['week']} | {p['class']} | {p['subject']} | {p['topic']} | {p['minutes']} |")
    Path("output/scheme_of_work.md").write_text("\n".join(scheme))
    print(to_md(lessons[0]))
    print(f"\nGenerated {len(lessons)} lesson plans and output/scheme_of_work.md")


if __name__ == "__main__":
    main()
