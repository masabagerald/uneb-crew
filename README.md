# UNEB Exam Generator

A multi-agent AI system built with CrewAI that generates ready-to-use UNEB-style exam sections for UCE (O-Level) and UACE (A-Level). Three specialist agents — Researcher, Question Writer, and Reviewer — collaborate sequentially to produce accurate, well-structured exam questions with full mark schemes.

---

## What it does

- Generates exam questions for any UNEB subject and topic
- Supports both UCE (O-Level, S1–S4) and UACE (A-Level, S5–S6)
- Produces a mix of question types: multiple choice, short answer, structured/essay
- Includes full mark schemes with expected answers and mark allocations
- Three-agent pipeline ensures research-backed, reviewed, publication-ready output
- Web UI with real-time agent progress indicator

---

## How it works

Three agents work sequentially — each reads the previous agent's output before doing its job:

```
Researcher
  ↓ content brief (key concepts, common errors, question angles)
Question Writer
  ↓ draft exam section (questions + mark schemes)
Reviewer
  ↓ corrected, approved final exam section
```

### The agents

**Researcher** — UNEB curriculum specialist. Produces a structured content brief covering key concepts, common student errors, typical UNEB question styles, and recommended cognitive levels for the topic.

**Question Writer** — UNEB examiner. Reads the research brief and drafts the full exam section with correctly allocated marks and detailed mark schemes. Targets a 30% recall / 40% application / 30% analysis difficulty distribution.

**Reviewer** — UNEB Chief Examiner. Checks factual accuracy, clarity, difficulty balance, and UNEB formatting conventions. Makes corrections directly and returns the final publication-ready section.

---

## Project structure

```
uneb-crew/
├── crew.py            # Agent definitions, tasks, and crew assembly
├── main.py            # FastAPI app — runs crew in thread pool
├── templates/
│   └── index.html     # Web UI with agent progress indicator
├── .env               # Environment variables (never commit this)
├── .env.example       # Template for required variables
└── README.md
```

---

## Requirements

- Python 3.10+
- OpenAI API key (GPT-4o)

---

## Installation

```bash
# 1. Navigate to project folder
cd uneb-crew

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install crewai crewai-tools fastapi uvicorn \
            python-multipart jinja2 python-dotenv
```

---

## Configuration

Copy `.env.example` to `.env`:

```env
OPENAI_API_KEY=sk-your-key-here
```

---

## Running the app

```bash
source venv/bin/activate
uvicorn main:app --reload
```

Open `http://localhost:8000` in your browser.

---

## Usage

Fill in the exam parameters in the web form:

| Field | Example |
|-------|---------|
| Subject | Biology, Mathematics, History, Chemistry |
| Topic | Cell Division and Mitosis, Quadratic Equations |
| Exam level | UCE — O-Level (S1–S4) or UACE — A-Level (S5–S6) |
| Number of questions | 3–15 |

Click **Generate exam section** and allow 60–120 seconds for all three agents to complete their work.

The output is displayed in a monospace format ready to copy into a Word document or exam paper template.

---

## Example inputs

```
Subject:    Biology
Topic:      Cell Division and Mitosis
Level:      UCE — O-Level
Questions:  5
```

```
Subject:    Mathematics
Topic:      Quadratic Equations and Inequalities
Level:      UACE — A-Level
Questions:  4
```

```
Subject:    History
Topic:      The Colonial Period in Uganda
Level:      UCE — O-Level
Questions:  6
```

---

## Output format

Each generated exam section follows UNEB formatting conventions:

```
Question 1 (4 marks)
[Question text]

Mark scheme:
[Expected answer]
[Mark allocation breakdown]

Question 2 (6 marks)
...
```

The Reviewer's note at the end explains any corrections made to the draft.

---

## Key CrewAI concepts used

**Sequential process** — tasks run in order. Each agent's output is automatically passed as context to the next agent. The Question Writer reads the Researcher's brief; the Reviewer reads the Writer's draft.

**Agent roles, goals, and backstories** — these shape the LLM's behaviour for each agent. The more specific and realistic they are, the more domain-appropriate the output. The Researcher speaks like a curriculum specialist; the Reviewer speaks like a Chief Examiner.

**Task expected_output** — tells CrewAI what a completed task looks like. Controls the length, structure, and format of each agent's output without enforcing a strict schema.

**ThreadPoolExecutor** — CrewAI's `crew.kickoff()` is synchronous. It runs in a thread pool so FastAPI's async event loop stays responsive during the 60–120 second generation.

---

## Extending the crew

### Add a fourth agent — PDF Formatter

```python
def make_formatter() -> Agent:
    return Agent(
        role="Exam Paper Formatter",
        goal="Convert the reviewed exam section into a clean, formatted PDF.",
        backstory="You are a UNEB administrative officer responsible for "
                  "typesetting and formatting official exam papers.",
        llm="gpt-4o",
    )
```

### Switch to hierarchical process

Replace `Process.sequential` with `Process.hierarchical` and add a manager:

```python
crew = Crew(
    agents=[researcher, writer, reviewer],
    tasks=[research_task, writing_task, review_task],
    process=Process.hierarchical,
    manager_llm="gpt-4o",   # manager delegates tasks dynamically
)
```

### Add web search to the Researcher

```python
from crewai_tools import SerperDevTool

researcher = Agent(
    ...
    tools=[SerperDevTool()],   # Researcher can now search current syllabus info
)
```

Requires a Serper API key in `.env`: `SERPER_API_KEY=your-key`

---

## Performance notes

- Each generation takes **60–120 seconds** — three sequential LLM calls with substantial prompts
- GPT-4o gives the best quality for UNEB-specific content
- You can switch to `gpt-4o-mini` in `crew.py` for faster, cheaper output at slightly lower quality:
  ```python
  Agent(llm="gpt-4o-mini", ...)
  ```
- Maximum 4 concurrent generations with the default `ThreadPoolExecutor(max_workers=4)`

---

## Difference from single-agent approach

A single agent asked to "research, write, and review" conflates all three roles and produces lower quality output — it cannot genuinely critique its own writing. The three-agent pipeline enforces role separation:

| Agent | What it brings |
|-------|---------------|
| Researcher | Domain knowledge depth, syllabus awareness |
| Question Writer | Examiner style, mark allocation conventions |
| Reviewer | Independent quality check, error correction |

The Reviewer reading the Writer's output cold — without knowing the original research — is what catches errors a self-reviewing agent would miss.

---

## Tech stack

| Component | Technology |
|-----------|------------|
| Multi-agent framework | CrewAI |
| LLM | OpenAI GPT-4o |
| Web framework | FastAPI |
| Async execution | ThreadPoolExecutor |
| Frontend | Vanilla HTML/CSS/JS |

---

