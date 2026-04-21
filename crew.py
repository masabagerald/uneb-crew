
import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from dotenv import load_dotenv

load_dotenv()

# ── Agents ─────────────────────────────────────────────────────

def make_researcher() -> Agent:
    return Agent(
        role="UNEB Curriculum Researcher",
        goal=(
            "Produce a focused, accurate content brief on the given topic "
            "that the Question Writer can use to write exam questions."
        ),
        backstory=(
            "You are a veteran Uganda National Examinations Board (UNEB) "
            "curriculum specialist with 15 years of experience mapping "
            "syllabus content for both UCE (O-Level) and UACE (A-Level) exams. "
            "You know exactly what depth and scope each level demands."
        ),
        verbose=True,
        allow_delegation=False,
        llm="gpt-4o",
    )

def make_question_writer() -> Agent:
    return Agent(
        role="UNEB Exam Question Writer",
        goal=(
            "Write a complete, well-structured exam section with questions "
            "and mark schemes that match the UNEB style and difficulty level."
        ),
        backstory=(
            "You are a seasoned UNEB examiner who has set papers for UCE and UACE "
            "for over a decade. You write clear, unambiguous questions, vary "
            "cognitive levels (recall, application, analysis), and always produce "
            "detailed mark schemes with expected answers and allocated marks."
        ),
        verbose=True,
        allow_delegation=False,
        llm="gpt-4o",
    )
def make_reviewer() -> Agent:
    return Agent(
        role="UNEB Chief Examiner / Reviewer",
        goal=(
            "Review the drafted exam section and return either an approved, "
            "polished final version or specific corrections the writer must make."
        ),
        backstory=(
            "You are a UNEB Chief Examiner responsible for quality assurance. "
            "You check that questions are factually correct, age-appropriate, "
            "free of ambiguity, properly balanced across difficulty levels, "
            "and faithfully follow UNEB formatting conventions."
        ),
        verbose=True,
        allow_delegation=False,
        llm="gpt-4o",
    )

# ── Tasks ───────────────────────────────────────────────────────
def make_research_task(agent: Agent, subject: str, topic: str, level: str) -> Task:
    return Task(
        description=f"""
Research the following for a UNEB exam question paper:

- Subject: {subject}
- Topic: {topic}
- Exam level: {level}

Produce a structured content brief covering:
1. The key concepts, definitions, and facts a student at this level must know.
2. Common misconceptions or areas where students typically lose marks.
3. Typical question styles UNEB uses for this subject and topic.
4. Suggested cognitive levels to target: recall, comprehension, application, analysis.

Be specific. Reference the UNEB syllabus depth for {level}.
""",
        expected_output=(
            "A structured content brief (400–600 words) covering key concepts, "
            "common student errors, and suggested question angles for this topic."
        ),
        agent=agent,
    )


def make_writing_task(agent: Agent, subject: str, topic: str,
                      level: str, num_questions: int) -> Task:
    return Task(
        description=f"""
Using the research brief provided, write a complete UNEB-style exam section.

Requirements:
- Subject: {subject}
- Topic: {topic}
- Exam level: {level}
- Number of questions: {num_questions}
- Mix of question types: multiple choice, short answer, and at least one
  structured/essay question (adjust based on subject norms).
- Each question must have marks allocated.
- Every question must be followed immediately by its mark scheme,
  including expected answers and how marks are awarded.
- Difficulty distribution: ~30% recall, ~40% application, ~30% analysis.
- Total marks should sum to a round number (e.g. 40, 50, or 100).

Format each question as:
  Question [N] ([X] marks)
  [Question text]

  Mark scheme:
  [Expected answer with mark allocation]
""",
        expected_output=(
            f"A complete exam section with {num_questions} questions, "
            "mark allocations, and full mark schemes in UNEB format."
        ),
        agent=agent,
    )

def make_review_task(agent: Agent, subject: str, topic: str, level: str) -> Task:
    return Task(
        description=f"""
Review the drafted {subject} exam section on {topic} for {level}.

Check for:
1. Factual accuracy — are all answers in the mark scheme correct?
2. Clarity — are questions unambiguous and age-appropriate?
3. Difficulty balance — is the 30/40/30 recall/application/analysis split maintained?
4. UNEB formatting — correct structure, mark allocations, mark scheme style.
5. Coverage — does the section adequately test the topic breadth?

If corrections are needed, make them directly and explain what you changed.
Return the final, publication-ready exam section.
""",
        expected_output=(
            "The final corrected and approved exam section, ready for use, "
            "with a brief reviewer's note explaining any changes made."
        ),
        agent=agent,
    )

# ── Crew factory ────────────────────────────────────────────────

def build_exam_crew(
    subject: str,
    topic: str,
    level: str,
    num_questions: int,
) -> Crew:
    researcher     = make_researcher()
    writer         = make_question_writer()
    reviewer       = make_reviewer()

    research_task  = make_research_task(researcher, subject, topic, level)
    writing_task   = make_writing_task(writer, subject, topic, level, num_questions)
    review_task    = make_review_task(reviewer, subject, topic, level)

    return Crew(
        agents=[researcher, writer, reviewer],
        tasks=[research_task, writing_task, review_task],
        process=Process.sequential,   # ← each task feeds into the next
        verbose=True,
    )

# ── Entry point ─────────────────────────────────────────────────

def generate_exam_section(
    subject: str,
    topic: str,
    level: str,
    num_questions: int,
) -> str:
    crew = build_exam_crew(subject, topic, level, num_questions)
    result = crew.kickoff()
    return str(result)

