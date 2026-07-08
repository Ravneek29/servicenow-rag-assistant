"""Retrieval + Claude answer generation with numbered citations."""

from langchain_core.prompts import ChatPromptTemplate

from app import config
from app.rag.store import get_vectorstore


def _build_llm():
    if config.LLM_PROVIDER == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(model=config.OLLAMA_MODEL, temperature=0, num_predict=1024)
    from langchain_anthropic import ChatAnthropic

    return ChatAnthropic(model=config.ANTHROPIC_MODEL, max_tokens=2048)

SYSTEM_PROMPT = """\
You are a ServiceNow knowledge assistant. Answer questions using ONLY the \
numbered documentation excerpts provided below.

Rules:
- Cite your sources inline using bracketed numbers that match the excerpts, \
e.g. "Incidents are prioritized by impact and urgency [1]."
- Every factual claim must carry at least one citation.
- If the excerpts do not contain enough information to answer, say so \
plainly and suggest what documentation the user could upload. Do not answer \
from general knowledge.
- Use ServiceNow terminology accurately (tables, modules, roles, states).
- Keep answers focused and well-structured; use short lists where helpful.

Documentation excerpts:
{context}"""

_prompt = ChatPromptTemplate.from_messages(
    [("system", SYSTEM_PROMPT), ("human", "{question}")]
)


def _format_context(results) -> str:
    blocks = []
    for i, (doc, _score) in enumerate(results, start=1):
        source = doc.metadata.get("source", "unknown")
        page = doc.metadata.get("page")
        location = f"{source}, page {page}" if page else source
        blocks.append(f"[{i}] ({location})\n{doc.page_content}")
    return "\n\n".join(blocks)


def _extractive_answer(results) -> str:
    """LLM-free fallback: return the most relevant passages verbatim."""
    lines = [
        "Answer generation is unavailable (no LLM credits configured), so "
        "here are the most relevant passages from your documentation:\n"
    ]
    for i, (doc, _score) in enumerate(results[:3], start=1):
        passage = " ".join(doc.page_content.split())
        if len(passage) > 600:
            passage = passage[:600].rsplit(" ", 1)[0] + "…"
        lines.append(f"{passage} [{i}]\n")
    return "\n".join(lines)


def answer_question(question: str, top_k: int | None = None) -> dict:
    store = get_vectorstore()
    results = store.similarity_search_with_relevance_scores(
        question, k=top_k or config.TOP_K
    )
    results = [(doc, score) for doc, score in results if score >= config.MIN_RELEVANCE]

    sources = [
        {
            "id": i,
            "source": doc.metadata.get("source", "unknown"),
            "page": doc.metadata.get("page"),
            "chunk": doc.metadata.get("chunk"),
            "score": round(float(score), 3),
            "snippet": doc.page_content[:400],
        }
        for i, (doc, score) in enumerate(results, start=1)
    ]

    if not results:
        return {
            "answer": (
                "The loaded documentation doesn't appear to cover this topic — "
                "no passages scored above the relevance threshold. Try "
                "rephrasing, or upload documentation that covers it."
            ),
            "sources": [],
        }

    if config.ANSWER_MODE != "extractive":
        try:
            chain = _prompt | _build_llm()
            response = chain.invoke(
                {"context": _format_context(results), "question": question}
            )
            return {"answer": response.text(), "sources": sources}
        except Exception:
            if config.ANSWER_MODE == "llm":
                raise
            # ANSWER_MODE == "auto": fall back to extractive search

    return {"answer": _extractive_answer(results), "sources": sources}
