"""The Claude Code Fundamentals skill: steps, items, and the stats the build checks."""

L, T, Q, S = "lesson", "task", "quiz", "scenario"


def step(n, slug, phase, minutes, title, summary, items):
    return dict(n=n, slug=slug, phase=phase, minutes=minutes, title=title, summary=summary, items=items)


CLAUDE_CODE = dict(
    id="claude-code", name="Claude Code Fundamentals", icon="⌨️", color="#d97757",
    tagline="Learn to drive Claude Code as a daily tool - the interactive console, permissions, headless scripting, "
            "project memory, plan mode, git work, custom commands, subagents, hooks, MCP, and settings - all hands-on, "
            "graded when you press Submit.",
    expected=dict(topics=20, tasks=23, quizzes=16, minutes=535),
    phases=[
        ("start", "Getting Started", "Set up, the interactive console, permissions, and headless runs with -p."),
        ("work", "Working with the Agent", "Clear instructions, project memory, context, plan mode, whole-codebase work, debugging, and git."),
        ("extend", "Extending Claude Code", "Custom slash commands, subagents, hooks, MCP servers, and settings."),
        ("automate", "Automation", "Headless Claude Code in scripts and on a schedule."),
        ("projects", "Claude Code Projects", "Three end-to-end jobs: build a CLI, fix a broken repo, configure a project."),
    ],
    steps=[
        step(1, "setup-and-prerequisites", "start", 20, "Claude Code: Setup & Prerequisites",
             "What Claude Code is, its two ways of running, and proving a machine is ready for it.",
             [(L, "What is Claude Code?"), (T, "Verify the prerequisites")]),
        step(2, "inside-the-console", "start", 30, "Claude Code: Inside the Console",
             "Launch the interactive console and use its slash commands - /init a project memory file, /model to "
             "switch models, and put the agent to work.",
             [(L, "Inside the console"), (T, "/init a project"), (T, "/model, then put it to work"),
              (Q, "Quick check: the console")]),
        step(3, "permissions-and-safety", "start", 25, "Claude Code: Permissions and Safety",
             "Learn how Claude Code asks before it acts, the four permission modes, and how to set an allowlist so an "
             "agent stays under your control.",
             [(L, "How permissions work"), (L, "Permission modes"), (T, "Set an allowlist"),
              (S, "Scenario: first run on an unfamiliar repo")]),
        step(4, "headless-with-p", "start", 25, "Claude Code: Headless with -p",
             "Run Claude Code as a one-shot Unix tool - capture answers, let it write real files, and compose it with "
             "the shell.",
             [(T, "Your first headless prompt"), (T, "Let Claude write a script"), (T, "Output formats and piping"),
              (Q, "Quick check: headless Claude Code")]),
        step(5, "instructing-the-agent", "work", 25, "Claude Code: Instructing the Agent",
             "Learn how to give Claude Code clear instructions, when to break a big task into steps, and how to "
             "iterate when the first result is close but not right.",
             [(L, "Giving good instructions"), (L, "When to break work up"), (T, "Write a clear brief"),
              (S, "Scenario: the code is almost right")]),
        step(6, "project-memory", "work", 25, "Claude Code: Project Memory",
             "Teach CLAUDE.md as the project memory Claude reads at the start of every session and what belongs in it.",
             [(L, "What CLAUDE.md is"), (L, "What to put in CLAUDE.md"), (T, "Write a project memory"),
              (Q, "Quick check: project memory")]),
        step(7, "managing-context", "work", 20, "Claude Code: Managing Context",
             "Teach what the context window is and how to keep it clean with /clear and /compact.",
             [(L, "The context window"), (L, "/clear and /compact"), (T, "Note when to clear and when to compact"),
              (Q, "Quick check: /clear vs /compact")]),
        step(8, "plan-mode", "work", 20, "Claude Code: Plan Mode",
             "Teach plan mode, where Claude explores read-only and proposes a plan you review before it changes anything.",
             [(L, "What plan mode is"), (T, "Plan before you build"), (S, "Scenario: refactoring an unfamiliar module")]),
        step(9, "working-across-a-codebase", "work", 25, "Claude Code: Working Across a Codebase",
             "Point Claude at a whole repo and let it search, read, and make coordinated edits across many files.",
             [(L, "Working across files"), (T, "Explore a small project with Claude"),
              (Q, "Quick check: working across a codebase")]),
        step(10, "debugging", "work", 25, "Claude Code: Debugging",
             "Show Claude an error or a failing test, let it find the cause and propose a fix, then run it again.",
             [(L, "Fixing bugs with Claude"), (T, "Fix a broken script with Claude"),
              (S, "Scenario: a fix you do not understand")]),
        step(11, "git-work", "work", 25, "Claude Code: Git Work",
             "Let Claude stage changes, write commit messages from the diff, and open PRs while you review before "
             "anything lands.",
             [(L, "Git work with Claude"), (T, "Commit a change with Claude"), (Q, "Quick check: git work with Claude")]),
        step(12, "custom-slash-commands", "extend", 20, "Claude Code: Custom Slash Commands",
             "Turn prompts you type often into reusable slash commands stored as markdown files.",
             [(L, "Custom slash commands"), (T, "Write a custom command"), (Q, "Quick check: custom slash commands")]),
        step(13, "subagents", "extend", 20, "Claude Code: Subagents",
             "Let Claude hand a scoped job to a subagent that runs in its own context and reports back.",
             [(L, "What subagents are"), (T, "Define a subagent"), (Q, "Quick check: subagents")]),
        step(14, "hooks", "extend", 25, "Claude Code: Hooks",
             "Run your own shell commands automatically on Claude Code lifecycle events like edits and prompts.",
             [(L, "What hooks are"), (T, "Add a hook"), (Q, "Quick check: hooks")]),
        step(15, "mcp-servers", "extend", 25, "Claude Code: MCP Servers",
             "Connect Claude Code to external tools and data through MCP servers you add, list, and remove from the "
             "command line.",
             [(L, "What MCP servers are"), (T, "Add an MCP server"), (Q, "Quick check: MCP servers")]),
        step(16, "settings", "extend", 20, "Claude Code: Settings",
             "Learn the settings hierarchy Claude Code reads and configure a project with a model and permission rules.",
             [(L, "The settings hierarchy"), (T, "Configure a project"), (Q, "Quick check: settings files")]),
        step(17, "automation", "automate", 25, "Claude Code: Automation",
             "Wrap headless Claude Code in scripts and schedule it so it runs real work without a human waiting on "
             "the keyboard.",
             [(L, "Claude in scripts"), (T, "Build an automation"), (S, "Scenario: scheduling Claude on a server")]),
        step(18, "project-build-a-cli-tool", "projects", 45, "Claude Code Project: Build a CLI Tool",
             "Build a small word-count CLI with Claude Code and document it in a CLAUDE.md.",
             [(T, "Build and document a word-count CLI")]),
        step(19, "project-fix-a-broken-repo", "projects", 45, "Claude Code Project: Fix a Broken Repo",
             "Use Claude Code to find and fix a real bug in a small repo until its test passes.",
             [(T, "Find and fix the bug until the test passes")]),
        step(20, "project-configure-a-project", "projects", 45, "Claude Code Project: Configure a Project",
             "Set up a repo for Claude Code end to end with a CLAUDE.md, a custom command, and a permissions allowlist.",
             [(T, "Configure a repo for Claude Code end to end")]),
    ],
)
