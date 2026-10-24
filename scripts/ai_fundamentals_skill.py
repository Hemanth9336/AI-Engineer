"""The AI Fundamentals skill: steps, items, and the stats the build checks."""

L, T, Q, S = "lesson", "task", "quiz", "scenario"

AI_FUNDAMENTALS = dict(
    id="ai-fundamentals", name="AI Fundamentals", icon="🧠", color="#8b5cf6",
    tagline="Learn how to actually use Gen AI to get work done in 2026 - prompting that works, choosing models, tools and "
            "agents, coding assistants, MCP, and working with your own data - all hands-on against real models through "
            "the lab's AI gateway.",
    expected=dict(topics=26, tasks=27, quizzes=25, minutes=955),
    phases=[
        ("foundations", "Generative AI Foundations", "What generative AI is, the tools you will meet, what they are good for, and how models behave."),
        ("api", "Calling Models over an API", "Send your own requests to real models with curl and read every part of the reply."),
        ("prompting", "Prompt Engineering", "Clear prompts, examples, step-by-step reasoning, roles, output control, and the refine loop."),
        ("working-with-models", "Working with Models", "Conversations and the context window, choosing a model, tokens and cost, and JSON output."),
        ("tools-and-agents", "Tools, Assistants and Agents", "Tool calling, coding assistants, MCP, the official SDKs, LangChain, and agents."),
        ("safety-and-data", "Safety and Your Own Data", "Hallucinations, prompt injection, privacy, and grounding answers in your own documents."),
        ("projects", "AI Fundamentals Projects", "Three small, real tools that put the whole skill to work."),
    ],
    steps=[
        dict(n=1, slug="what-is-generative-ai", phase="foundations", minutes=20,
             title="What is Generative AI",
             summary="How generative AI differs from the rule-following software you already know, the kinds of content it "
                     "can create, and where large language models fit in.",
             items=[(L, "Generative AI versus traditional software"), (L, "The kinds of generative AI"),
                    (L, "Where LLMs fit in"), (Q, "Quick check: what is generative AI")]),
        dict(n=2, slug="the-ai-tool-landscape", phase="foundations", minutes=20,
             title="The AI tool landscape",
             summary="A tour of the AI tools you will actually run into - chat assistants like ChatGPT, Claude, and Gemini, "
                     "coding assistants, AI search, AI built into everyday apps, and how free versus paid tiers work.",
             items=[(L, "Chat assistants"), (L, "Coding assistants and AI inside your apps"),
                    (L, "Free, paid, and choosing a tool"), (Q, "Quick check: the tool landscape")]),
        dict(n=3, slug="what-you-can-do-with-ai", phase="foundations", minutes=20,
             title="What you can do with AI",
             summary="The practical payoff - the everyday jobs people hand to AI, the same help aimed at real engineering "
                     "work, and an honest look at where AI falls short so you use it with your eyes open.",
             items=[(L, "Everyday uses"), (L, "Uses at work"), (L, "Where AI falls short"),
                    (Q, "Quick check: using AI well")]),
        dict(n=4, slug="ai-absolute-basics", phase="foundations", minutes=45,
             title="AI absolute basics",
             summary="What a large language model actually is, what tokens are, why tokens drive LLM pricing, open versus "
                     "frontier models, and why models hallucinate - with hands-on work using the claude command.",
             items=[(L, "What is an LLM"), (L, "Tokens"), (L, "Why tokens matter"), (T, "Talk to the AI"),
                    (L, "Open models vs frontier models"), (L, "Hallucinations and limits"),
                    (Q, "Quick check: how models behave")]),
        dict(n=5, slug="calling-llms-over-an-api", phase="api", minutes=40,
             title="Calling LLMs over an API",
             summary="Why real AI work happens in code, and how to send your own requests to real models with curl - the "
                     "request, the response JSON, and the reply path you'll use constantly.",
             items=[(L, "Why call an LLM over an API"), (T, "Your first request with curl"),
                    (T, "Send your own request"), (T, "Try a different model"), (T, "Understand max_tokens limits"),
                    (Q, "Quick check: the API call")]),
        dict(n=6, slug="writing-prompts-that-work", phase="prompting", minutes=35,
             title="Writing prompts that work",
             summary="What separates a clear prompt from a vague one, how the system and user roles differ, and how being "
                     "specific gets you better answers.",
             items=[(L, "What makes a good prompt"), (L, "System and user messages"), (L, "Being specific"),
                    (T, "Write a clear prompt"), (Q, "Quick check: prompting basics")]),
        dict(n=7, slug="prompting-with-examples", phase="prompting", minutes=35,
             title="Prompting with examples",
             summary="The difference between asking with no examples and giving a few, why a couple of examples steer the "
                     "model, and how to write examples it will copy faithfully.",
             items=[(L, "Zero-shot vs few-shot"), (L, "Giving good examples"), (T, "Write a few-shot prompt"),
                    (Q, "Quick check: few-shot prompting")]),
        dict(n=8, slug="step-by-step-prompting", phase="prompting", minutes=35,
             title="Step-by-step prompting",
             summary="Ask a model to work through multi-step problems one step at a time so its reasoning stays on track "
                     "and its answers get more accurate.",
             items=[(L, "Why step-by-step helps"), (L, "Asking for reasoning"), (T, "Solve a problem step by step"),
                    (Q, "Quick check: step-by-step prompting")]),
        dict(n=9, slug="ai-roles-and-personas", phase="prompting", minutes=30,
             title="AI roles and personas",
             summary="How giving a model a role focuses its expertise and tone, and how framing for a tone or audience "
                     "changes the way it explains without changing the facts.",
             items=[(L, "Giving the AI a role"), (L, "Shaping tone and audience"),
                    (T, "Write a role prompt for a real task"), (Q, "Quick check: roles and framing")]),
        dict(n=10, slug="controlling-the-output", phase="prompting", minutes=35,
             title="Controlling the output",
             summary="How to constrain the shape and length of a model's answer, and how delimiters keep your instructions "
                     "separate from the text you want processed.",
             items=[(L, "Asking for a format"), (L, "Using delimiters"), (T, "Generate a formatted checklist"),
                    (Q, "Quick check: format and delimiters")]),
        dict(n=11, slug="improving-your-prompts", phase="prompting", minutes=35,
             title="Improving your prompts",
             summary="Why a first prompt often disappoints, how to read a weak answer and spot the cause, and the refine "
                     "loop that turns a rough attempt into the answer you wanted.",
             items=[(L, "Why first prompts fail"), (L, "Diagnosing a weak answer"), (L, "The refine loop"),
                    (T, "Fix a failing prompt"), (S, "Scenario: picking the next fix")]),
        dict(n=12, slug="multi-turn-conversations", phase="working-with-models", minutes=35,
             title="Multi-turn conversations",
             summary="How a chat is just a growing messages array, what the context window is and why it fills up, and "
                     "how to keep long conversations working.",
             items=[(L, "Multi-turn conversations"), (L, "The context window"), (L, "Managing long conversations"),
                    (T, "Hold a conversation"), (Q, "Quick check: conversations and the window")]),
        dict(n=13, slug="choosing-a-model", phase="working-with-models", minutes=35,
             title="Choosing a model",
             summary="Why models trade speed against quality, what each of the five lab models is good for, and how to "
                     "match a model to the task in front of you.",
             items=[(L, "Not all models are equal"), (L, "The five lab models"), (L, "Matching a model to the task"),
                    (T, "Compare two models on one prompt"), (S, "Scenario: choosing a model for a batch job")]),
        dict(n=14, slug="tokens-and-cost", phase="working-with-models", minutes=35,
             title="Tokens and cost",
             summary="How per-token pricing actually adds up, how to read every field in the usage block, and the concrete "
                     "levers that keep a request lean.",
             items=[(L, "How LLM pricing works"), (L, "Reading the usage block in detail"), (L, "Keeping requests lean"),
                    (T, "Measure a request's token usage"), (Q, "Quick check: tokens and cost")]),
        dict(n=15, slug="structured-output-with-json", phase="working-with-models", minutes=35,
             title="Structured output with JSON",
             summary="How to make a model return machine-readable JSON instead of prose, prompt it for a fixed shape, and "
                     "validate the result with jq.",
             items=[(L, "Why structured output"), (L, "Asking a model for JSON"), (T, "Get parseable JSON from a model"),
                    (Q, "Quick check: structured output")]),
        dict(n=16, slug="tool-calling", phase="tools-and-agents", minutes=35,
             title="Tool Calling",
             summary="How the model asks your program to run functions you define, so AI can fetch live data and act on "
                     "the world instead of just guessing.",
             items=[(L, "What tool calling is"), (L, "How the tool loop works"), (T, "Let the model call a tool"),
                    (Q, "Quick check: tool calling")]),
        dict(n=17, slug="ai-coding-assistants", phase="tools-and-agents", minutes=35,
             title="AI Coding Assistants",
             summary="What AI coding assistants do and how to use claude from the terminal to write, explain, and fix code.",
             items=[(L, "AI as a coding assistant"), (L, "Using claude in the terminal"), (T, "Write a script with claude"),
                    (Q, "Quick check: coding assistants")]),
        dict(n=18, slug="model-context-protocol", phase="tools-and-agents", minutes=35,
             title="Model Context Protocol",
             summary="What MCP is, how it builds on tool calling, and how to register a real MCP server with claude so the "
                     "assistant can act on external tools and data.",
             items=[(L, "What is MCP"), (L, "claude mcp add and claude mcp list"), (T, "Register the GitHub MCP server"),
                    (Q, "Quick check: MCP")]),
        dict(n=19, slug="using-the-api-in-real-code", phase="tools-and-agents", minutes=45,
             title="Using the API in real code",
             summary="Move from curl to real code - call the API with the OpenAI and Anthropic Python SDKs, keep your key "
                     "safe, and automate a task across a whole folder of inputs in one run.",
             items=[(T, "The OpenAI SDK in Python"), (T, "The Anthropic SDK and the Messages API"),
                    (S, "Scenario: the key in the script"), (T, "Automate a batch of files"),
                    (Q, "Quick check: keys and the SDK")]),
        dict(n=20, slug="langchain-basics", phase="tools-and-agents", minutes=35,
             title="LangChain basics",
             summary="What LangChain is, the pieces of a simple chain (a chat model, a prompt template, and piping them "
                     "together), and building one that runs against the API.",
             items=[(L, "What is LangChain"), (L, "Your first chain"), (T, "Build a simple chain"),
                    (Q, "Quick check: LangChain")]),
        dict(n=21, slug="building-agents", phase="tools-and-agents", minutes=35,
             title="Building Agents",
             summary="What an AI agent is, how a model runs in a loop and calls tools to reach a goal, and how to build a "
                     "small LangChain agent with one tool.",
             items=[(L, "What is an agent"), (L, "A simple LangChain agent"), (T, "Build a simple agent"),
                    (S, "Scenario: how much freedom to give an agent")]),
        dict(n=22, slug="limitations-and-safety", phase="safety-and-data", minutes=30,
             title="Limitations and safety",
             summary="How to reduce hallucinations, why prompt injection makes model output untrustworthy, what leaves your "
                     "machine when you send a prompt, and when the safe move is to verify or refuse.",
             items=[(L, "Reducing hallucinations"), (L, "Prompt injection"), (L, "Privacy and your data"),
                    (S, "Scenario: an instruction hidden in the data"), (Q, "Quick check: limitations and safety")]),
        dict(n=23, slug="using-your-own-data", phase="safety-and-data", minutes=35,
             title="Using your own data",
             summary="How to ground a model in your own facts so it answers about your systems instead of guessing, what "
                     "RAG means from a user's point of view, and answering a real question from a local document.",
             items=[(L, "Grounding answers in your data"), (L, "What RAG is"), (T, "Answer a question from a document"),
                    (Q, "Quick check: using your own data")]),
        dict(n=24, slug="project-support-ticket-triage-tool", phase="projects", minutes=60,
             title="Project: support ticket triage tool",
             summary="Capstone. Build a small tool that reads raw support tickets and sorts each one into a category and "
                     "priority as clean JSON, using prompting and structured output against a real model.",
             items=[(T, "Build a support ticket triage tool")]),
        dict(n=25, slug="project-log-explainer-cli", phase="projects", minutes=60,
             title="Project: log explainer CLI",
             summary="Capstone. Build a command-line tool that reads a log file and returns a short plain-English summary "
                     "and likely cause, using a role prompt against a real model.",
             items=[(T, "Build a log explainer CLI")]),
        dict(n=26, slug="project-grounded-runbook-assistant", phase="projects", minutes=60,
             title="Project: grounded runbook assistant",
             summary="Capstone. Build a question-answering tool that answers only from a runbook you give it and admits "
                     "when the answer is not there, putting grounding and honest limits into practice.",
             items=[(T, "Build a grounded runbook assistant")]),
    ],
)
