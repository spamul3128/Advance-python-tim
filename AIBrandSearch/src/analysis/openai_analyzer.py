"""
Comparative analysis of SERP + LLM results using OpenAI.
Produces readable summaries, recommendations, and insights.
"""

from src.models import LLMResult, SERPResult

# Truncate long answers for context window; keep full content for key models if needed
MAX_ANSWER_CHARS = 4000


def _build_context(
    query: str,
    llm_results: list[LLMResult],
    serp_results: list[SERPResult] | None,
) -> str:
    """Build a single text block for the LLM with all SERP and AI answers."""
    sections = []

    sections.append(f"## Original search query\n{query}\n")

    if serp_results:
        sections.append("## Google search results (organic)")
        for r in serp_results:
            sections.append(
                f"[{r.position}] {r.title}\nURL: {r.url}\nSnippet: {r.snippet}\n"
            )
        sections.append("")

    sections.append("## Answers from AI search / LLM products")
    for r in llm_results:
        if r.status != "success" or not r.answer_text:
            sections.append(f"### {r.model_name}\n(No response or error)\n")
            continue
        text = r.answer_text
        if len(text) > MAX_ANSWER_CHARS:
            text = text[:MAX_ANSWER_CHARS] + "\n[... truncated ...]"
        sections.append(f"### {r.model_name}\n{text}\n")

    return "\n".join(sections)


def _build_system_prompt(tracking_keywords: list[str]) -> str:
    terms_str = ", ".join(f'"{k}"' for k in tracking_keywords[:30])  # cap for prompt size
    return f"""You are an analyst whose main job is to report on visibility of specific brands/tools across search and AI answers.

The tracked terms (brands/tools) the user cares about are: {terms_str}.

You will receive: the original search query, Google organic results (title, URL, snippet), and full answers from several AI products (ChatGPT, Perplexity, Gemini, Grok, Copilot, etc.).

Your response MUST be built around these tracked terms. The primary insight the user wants is: for each of these terms, who mentions it and how (Google vs each AI, position/order, positive/neutral/absent).

Structure your response as follows:

1. **Keyword visibility (required – do this first)**  
   For each tracked term, in a short block or row, state:
   - Whether it appears in Google results (which positions/titles) and/or in each AI answer.
   - If in an AI answer: roughly where (e.g. first in a list, middle of narrative).
   - If not mentioned anywhere, say so explicitly (e.g. "Not mentioned in any source").
   Cover every tracked term. This section is the main deliverable.

2. **Summary**  
   One short paragraph: what Google emphasizes vs what the AI answers emphasize, specifically in relation to the tracked terms.

3. **Gaps and recommendations**  
   Which tracked terms are under-represented in AI answers vs Google (or vice versa)? One or two concrete recommendations for improving or monitoring visibility of these terms.

Rules: Use the exact tracked term names. Be concise. Lead with keyword visibility; other sections support that insight. Use bullet points and clear headings."""


def _build_user_prompt(context: str, tracking_keywords: list[str]) -> str:
    terms_str = ", ".join(f'"{k}"' for k in tracking_keywords[:30])
    return f"""The tracked terms to analyze are: {terms_str}.

Your response must focus on these terms. Start with a "Keyword visibility" section where you go through each term and state where it appears (Google and each AI) and how. Then add a brief summary and gaps/recommendations. Do not give a long general summary—prioritize the per-term visibility breakdown.

Data below.

{context}"""


def run_comparative_analysis(
    query: str,
    llm_results: list[LLMResult],
    serp_results: list[SERPResult] | None,
    *,
    api_key: str,
    model: str = "gpt-4",
    tracking_keywords: list[str] | None = None,
) -> str:
    """
    Call OpenAI to analyze SERP + LLM results and return comparative analysis text.
    Focuses on the given tracking_keywords (brands/tools to analyze). Uses api_key from OPENAI_API_KEY in .env.
    """
    if not api_key or not api_key.strip():
        return "Error: No OpenAI API key provided. Set OPENAI_API_KEY in your .env file."

    if not llm_results and not (serp_results or []):
        return "No data to analyze: run the LLM comparison first, and optionally fetch SERP."

    keywords = tracking_keywords or []
    context = _build_context(query, llm_results, serp_results or [])
    system = _build_system_prompt(keywords)
    user = _build_user_prompt(context, keywords)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key.strip())
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_completion_tokens=2000,
        )
        choice = response.choices[0] if response.choices else None
        if not choice or not choice.message:
            return "OpenAI returned no choices. Try a different model or check the API status."

        content = choice.message.content
        if content is None:
            reason = getattr(choice, "finish_reason", None) or "unknown"
            return f"OpenAI returned an empty response (finish_reason: {reason}). Try a different model (e.g. gpt-4o-mini) or check content filters."

        # Some models return content as a list of parts (e.g. multimodal)
        if isinstance(content, list):
            text_parts = [
                part.get("text", "") if isinstance(part, dict) else str(part)
                for part in content
            ]
            content = "".join(text_parts)

        text = (content or "").strip()
        if not text:
            return "OpenAI returned an empty response. Try a different model or reduce the amount of input data."
        return text
    except Exception as e:
        return f"Analysis failed: {e}"
