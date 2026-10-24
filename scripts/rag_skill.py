"""The RAG skill: steps, items, and the stats the build checks."""

L, T, Q, S = "lesson", "task", "quiz", "scenario"

RAG = dict(
    id="rag", name="RAG", icon="🔎", color="#10b981",
    tagline="Build Retrieval-Augmented Generation from nothing - ground a model in your own documents, create embeddings, "
            "search by meaning, chunk real files, run a vector database, and ship a working RAG pipeline by hand, on "
            "Chroma, and with LangChain.",
    expected=dict(topics=16, tasks=22, quizzes=14, minutes=765),
    phases=[
        ("start", "The Problem and Your Tools", "Why models can't answer about your data, the Python you need, and grounding a prompt."),
        ("search", "Search by Meaning", "Embeddings, cosine similarity, and semantic search - the retrieval half of RAG."),
        ("indexing", "Indexing Real Documents", "Chunking files, a vector store built by hand, and Chroma."),
        ("pipeline", "The RAG Pipeline", "Every piece connected, moved onto Chroma, and measured."),
        ("langchain", "RAG with LangChain", "The same pipeline with the library teams use at work."),
        ("projects", "RAG Projects", "Three complete assistants that answer from documents - and refuse when they can't."),
    ],
    steps=[
        dict(n=1, slug="the-problem-rag-solves", phase="start", minutes=40,
             title="The Problem RAG Solves",
             summary="Why a model can't answer questions about your team's own documents, the one move that fixes it - "
                     "putting the document in the prompt - and the three words behind RAG.",
             items=[(L, "The AI does not know your data"), (L, "Ask without the document, then with it"),
                    (T, "Make the model answer from your document"), (L, "What RAG is, in one picture"),
                    (Q, "Quick check: the problem RAG solves")]),
        dict(n=2, slug="tools-you-will-use", phase="start", minutes=35,
             title="Tools You Will Use",
             summary="How this course works, and a short Python refresher - calling a model from a script, the one "
                     "skill every later topic builds on.",
             items=[(L, "How this course works"), (L, "Calling a model from Python"), (T, "Write your ask script"),
                    (Q, "Quick check: tools")]),
        dict(n=3, slug="grounding-a-prompt", phase="start", minutes=40,
             title="Grounding a Prompt",
             summary="How to write a prompt so the model answers from your document and nothing else - and admits it "
                     "when the answer is not there.",
             items=[(L, "Putting facts in the prompt"), (L, "Two rules that make grounding safe"),
                    (L, "A grounded prompt, worked through"), (T, "Ground a prompt yourself"),
                    (Q, "Quick check: grounding")]),
        dict(n=4, slug="embeddings", phase="search", minutes=40,
             title="Embeddings",
             summary="How text becomes a list of numbers that captures meaning - the piece of math that lets a computer "
                     "find the right document.",
             items=[(L, "What is an embedding"), (L, "Get your first embedding"), (T, "Embed a sentence"),
                    (Q, "Quick check: embeddings")]),
        dict(n=5, slug="measuring-similarity", phase="search", minutes=40,
             title="Measuring Similarity",
             summary="Cosine similarity - the small piece of math that turns two vectors into one score, with a "
                     "ready-to-use Python function.",
             items=[(L, "Cosine similarity"), (L, "Comparing two sentences, worked through"), (T, "Score two pairs"),
                    (Q, "Quick check: similarity")]),
        dict(n=6, slug="semantic-search", phase="search", minutes=35,
             title="Semantic Search",
             summary="One query against many candidates - embed everything, score everything, sort. Search by meaning "
                     "in forty lines of Python.",
             items=[(L, "Search by meaning, not words"), (L, "Ranking many candidates, worked through"),
                    (T, "Rank support messages"), (Q, "Quick check: semantic search")]),
        dict(n=7, slug="chunking", phase="indexing", minutes=50,
             title="Chunking",
             summary="Why long documents get cut into pieces before embedding, how to choose the cuts, and how to chunk "
                     "and embed a real document.",
             items=[(L, "Why not embed the whole document"), (L, "Chunk size and overlap"),
                    (L, "Chunking a document, worked through"), (T, "Chunk a handbook"),
                    (L, "Embedding the chunks"), (T, "Embed your chunks"), (Q, "Quick check: chunking")]),
        dict(n=8, slug="build-your-own-vector-store", phase="indexing", minutes=50,
             title="Build Your Own Vector Store",
             summary="Give the text-plus-vector index a proper home in sqlite, and query it - the store and query "
                     "phases of every vector database, built by hand.",
             items=[(L, "What a vector store does"), (L, "Storing vectors in sqlite, worked through"),
                    (T, "Build the store"), (L, "Querying the store, worked through"), (T, "Query the store"),
                    (Q, "Quick check: your vector store")]),
        dict(n=9, slug="chroma-a-real-vector-database", phase="indexing", minutes=50,
             title="Chroma, a Real Vector Database",
             summary="Install Chroma, put your chunks in a collection, and query it - the same store and query phases "
                     "you built by hand, now as two function calls.",
             items=[(L, "Why a real vector database"), (L, "Creating a collection, worked through"),
                    (T, "Add your chunks to Chroma"), (L, "Querying Chroma, worked through"),
                    (T, "Query your collection"), (Q, "Quick check: Chroma")]),
        dict(n=10, slug="the-full-rag-pipeline", phase="pipeline", minutes=50,
             title="The Full RAG Pipeline",
             summary="Connect every piece you built - chunk, embed, store, retrieve, ground - into one working pipeline "
                     "that answers questions and admits what it cannot answer.",
             items=[(L, "The three phases together"), (L, "A tiny pipeline, worked through"),
                    (T, "Build your own pipeline"), (S, "Scenario: retrieval returned the wrong chunk"),
                    (Q, "Quick check: the pipeline")]),
        dict(n=11, slug="rag-on-chroma", phase="pipeline", minutes=45,
             title="RAG on Chroma",
             summary="Swap the hand-built store for Chroma inside your pipeline, use top-k retrieval, and run a bigger "
                     "document set - the same machine, production parts.",
             items=[(L, "Swapping the store"), (L, "The pipeline on Chroma, worked through"),
                    (T, "Rebuild your pipeline on Chroma"), (Q, "Quick check: RAG on Chroma")]),
        dict(n=12, slug="evaluating-rag", phase="pipeline", minutes=50,
             title="Evaluating RAG",
             summary="How to know your RAG system actually works - measure whether retrieval finds the right chunk, and "
                     "whether the answers use it.",
             items=[(L, "How you know your RAG works"), (L, "A small eval set"),
                    (L, "Scoring retrieval, worked through"), (T, "Measure your retrieval hit rate"),
                    (L, "Scoring answers, worked through"), (T, "Score your answers"),
                    (Q, "Quick check: evaluating RAG")]),
        dict(n=13, slug="rag-with-langchain", phase="langchain", minutes=60,
             title="RAG with LangChain",
             summary="The pipeline one more time, with the library teams use - a text splitter, a Chroma vector store "
                     "wrapper, a retriever, and one chain that does it all.",
             items=[(L, "What LangChain gives you"), (L, "Installing LangChain and splitting, worked through"),
                    (T, "Split a document with the text splitter"),
                    (L, "The vector store and retriever, worked through"), (T, "Build a retriever"),
                    (L, "The full chain, worked through"), (T, "Build the RAG chain"),
                    (Q, "Quick check: RAG with LangChain")]),
        dict(n=14, slug="project-docs-qa-bot", phase="projects", minutes=60,
             title="Project: Docs Q&A Bot",
             summary="Build a complete question-answering bot over a folder of markdown documents - index, retrieve, "
                     "ground, refuse. Everything from the course, one working tool.",
             items=[(T, "Project: Docs Q&A Bot")]),
        dict(n=15, slug="project-support-knowledge-assistant", phase="projects", minutes=60,
             title="Project: Support Knowledge Assistant",
             summary="Point RAG at a support inbox - retrieve the right knowledge-base article for each incoming ticket "
                     "and write a grounded reply.",
             items=[(T, "Project: Support Knowledge Assistant")]),
        dict(n=16, slug="project-runbook-assistant-that-knows-its-limits", phase="projects", minutes=60,
             title="Project: Runbook Assistant That Knows Its Limits",
             summary="The final build - a LangChain RAG assistant over an ops runbook, graded as hard on its refusals "
                     "as on its answers.",
             items=[(T, "Project: Runbook Assistant That Knows Its Limits")]),
    ],
)
