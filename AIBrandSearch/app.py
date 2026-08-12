"""
LLM Mentions Tracker Demo — Streamlit entrypoint.
Single-page app: sidebar controls, main area shows results (signals table, tabs, SERP, export).
"""

import json
import os
from datetime import datetime
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from src.config import DEFAULT_TRACKING_KEYWORDS, LLM_ORDER, LLM_SCRAPERS
from src.models import LLMResult, SERPResult
from src.parser.parser import parse_result
from src.runner.prompt_runner import run_all_llms_with_progress_sync, run_async
from src.runner.bulk_runner import run_bulk, save_single_run, save_serp_to_run, save_analysis_to_run, RUNS_DIR
from src.api.serp import fetch_serp
from src.ui_helpers import build_export_json, highlight_keywords
from src.analysis import run_comparative_analysis, generate_prompts_from_topic, save_prompts_to_file
from src.run_loader import load_run_from_dir

st.set_page_config(page_title="LLM Mentions Tracker", layout="wide")

# Custom CSS: dark theme polish, model colors, mention highlights
st.markdown(
    """
    <style>
    .mention { background: rgba(255, 193, 7, 0.35); padding: 0 2px; border-radius: 2px; }
    .model-badge { padding: 4px 10px; border-radius: 6px; font-weight: 600; font-size: 0.9em; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stDataFrame { font-size: 0.9rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


# Country codes to display names for "Search location"
COUNTRY_DISPLAY = {
    "us": "United States",
    "uk": "United Kingdom",
    "de": "Germany",
    "fr": "France",
    "ca": "Canada",
    "au": "Australia",
}


def get_api_token() -> str | None:
    """API token from .env (via python-dotenv)."""
    return os.environ.get("BRIGHT_DATA_API_TOKEN") or None


def get_openai_api_key() -> str | None:
    """OpenAI API key from .env for comparative analysis."""
    return os.environ.get("OPENAI_API_KEY") or None


def render_sidebar(
    prompt: str,
    models: list[str],
    country: str,
    keywords_text: str,
) -> tuple[str, list[str], str | None, list[str], bool, bool, any, bool]:
    """Sidebar: prompt, models, country, keywords, run buttons, bulk file."""
    st.sidebar.title("LLM Mentions Tracker")
    st.sidebar.caption("Compare prompts across ChatGPT, Perplexity, Gemini, Grok, Copilot")

    prompt_input = st.sidebar.text_area(
        "Prompt",
        value=prompt,
        height=100,
        placeholder="e.g. What tools monitor search results in LLMs?",
    )
    model_options = [LLM_SCRAPERS[k]["name"] for k in LLM_ORDER]
    model_keys = list(LLM_ORDER)
    selected_names = st.sidebar.multiselect(
        "Models",
        options=model_options,
        default=model_options,
        format_func=lambda x: x,
    )
    selected_models = [model_keys[model_options.index(n)] for n in selected_names if n in model_options]

    countries = ["us", "uk", "de", "fr", "ca", "au", None]
    country_labels = ["US", "UK", "DE", "FR", "CA", "AU", "Default"]
    country_idx = countries.index(country) if country in countries else 0
    country_sel = st.sidebar.selectbox(
        "Country",
        options=range(len(countries)),
        index=country_idx,
        format_func=lambda i: country_labels[i],
    )
    country_value = countries[country_sel]

    keywords_input = st.sidebar.text_area(
        "Tracking keywords (one per line or comma-separated)",
        value=keywords_text,
        height=120,
    )
    keywords_list = [
        x.strip()
        for line in keywords_input.replace(",", "\n").splitlines()
        for x in [line.strip()]
        if x
    ] or DEFAULT_TRACKING_KEYWORDS

    run_clicked = st.sidebar.button("Run Across All Models", type="primary")
    st.sidebar.divider()
    st.sidebar.subheader("Bulk run")
    bulk_file = st.sidebar.file_uploader("Upload prompt list (JSON)", type=["json"])
    bulk_clicked = st.sidebar.button("Run Bulk")
    simulate_clicked = st.sidebar.button("Simulate Daily Run")

    return (
        prompt_input,
        selected_models,
        country_value,
        keywords_list,
        run_clicked,
        bulk_clicked,
        bulk_file,
        simulate_clicked,
    )


def render_signals_table(parsed_list: list) -> None:
    """Section 2: Extracted signals summary table (money shot)."""
    st.subheader("Extracted signals summary")
    rows = []
    for p in parsed_list:
        pos_str = ", ".join(
            f"{k}:{v}" for k, v in sorted(p.mention_positions.items(), key=lambda x: (x[1], x[0])) if v > 0
        ) or "—"
        rows.append({
            "Model": p.model_name,
            "Mentioned tools": ", ".join(p.mentioned_tools) or "—",
            "Position": pos_str,
            "Answer shape": p.answer_shape,
            "Word count": p.word_count,
        })
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)


def render_response_tabs(results: list[LLMResult], keywords: list[str]) -> None:
    """Section 3: Tabs per model with highlighted answer text."""
    tab_names = [r.model_name for r in results]
    tabs = st.tabs(tab_names)
    for tab, result in zip(tabs, results):
        with tab:
            if result.status != "success":
                st.error(result.error_message or result.status)
            else:
                highlighted = highlight_keywords(result.answer_text or "", keywords)
                st.markdown(highlighted, unsafe_allow_html=True)


def main():
    # Session state
    if "results" not in st.session_state:
        st.session_state.results = None
    if "parsed" not in st.session_state:
        st.session_state.parsed = None
    if "serp" not in st.session_state:
        st.session_state.serp = None
    if "analysis_text" not in st.session_state:
        st.session_state.analysis_text = None
    if "last_prompt" not in st.session_state:
        st.session_state.last_prompt = ""
    if "last_country" not in st.session_state:
        st.session_state.last_country = None
    if "keywords_used" not in st.session_state:
        st.session_state.keywords_used = DEFAULT_TRACKING_KEYWORDS
    if "last_run_id" not in st.session_state:
        st.session_state.last_run_id = None
    if "last_run_prompts" not in st.session_state:
        st.session_state.last_run_prompts = []
    if "selected_prompt_index" not in st.session_state:
        st.session_state.selected_prompt_index = 0
    if "generated_prompts" not in st.session_state:
        st.session_state.generated_prompts = None
    if "generated_keywords" not in st.session_state:
        st.session_state.generated_keywords = None

    default_prompt = "What tools monitor search results in LLMs?"
    keywords_default = "\n".join(DEFAULT_TRACKING_KEYWORDS)

    (
        prompt,
        selected_models,
        country,
        keywords_list,
        run_clicked,
        bulk_clicked,
        bulk_file,
        simulate_clicked,
    ) = render_sidebar(default_prompt, list(LLM_ORDER), "us", keywords_default)

    api_token = get_api_token()
    if not api_token:
        st.sidebar.warning("Set BRIGHT_DATA_API_TOKEN in your .env file")
    st.sidebar.divider()

    # Past runs — always visible in sidebar so users can load a run anytime
    runs_dir = RUNS_DIR
    if runs_dir.exists():
        st.sidebar.subheader("Past runs")
        subdirs = sorted([d for d in runs_dir.iterdir() if d.is_dir()], reverse=True)[:20]
        if not subdirs:
            st.sidebar.caption("No saved runs yet. Run a comparison to create one.")
        for d in subdirs:
            meta_file = d / "run-metadata.json"
            label = d.name
            if meta_file.exists():
                try:
                    with open(meta_file, encoding="utf-8") as f:
                        meta = json.load(f)
                    prompt_count = meta.get("prompt_count", 0)
                    models_count = len(meta.get("models", []))
                    prompts_preview = (meta.get("prompts") or [])[:1]
                    first_prompt = (prompts_preview[0][:50] + "…") if prompts_preview and len(str(prompts_preview[0])) > 50 else (prompts_preview[0] if prompts_preview else "")
                    label = f"{d.name} — {prompt_count} prompt(s), {models_count} models"
                    if first_prompt:
                        label += f" · \"{first_prompt}\""
                except Exception:
                    pass
            if st.sidebar.button(label, key=f"load_run_{d.name}", use_container_width=True):
                loaded = load_run_from_dir(d)
                if loaded:
                    st.session_state.results = loaded["results"]
                    st.session_state.parsed = loaded["parsed"]
                    st.session_state.last_prompt = loaded["prompt"]
                    st.session_state.last_country = loaded["country"]
                    st.session_state.serp = loaded.get("serp")
                    st.session_state.keywords_used = (
                        loaded.get("tracking_keywords") or DEFAULT_TRACKING_KEYWORDS
                    )
                    st.session_state.analysis_text = loaded.get("analysis_text")
                    st.session_state.last_run_id = d.name
                    st.session_state.last_run_prompts = loaded.get("prompts_list") or []
                    st.session_state.selected_prompt_index = 0
                    st.rerun()
                else:
                    st.sidebar.error(f"Could not load run {d.name}")
    st.sidebar.divider()

    # Generate batch prompts from topic (OpenAI)
    openai_key = get_openai_api_key()
    st.sidebar.subheader("Generate batch prompts")
    if not openai_key:
        st.sidebar.caption("Set OPENAI_API_KEY in .env to use this.")
    topic_input = st.sidebar.text_input("Topic for generating prompts", placeholder="e.g. SEO tools for e-commerce")
    gen_count = st.sidebar.number_input("Number of prompts", min_value=1, max_value=50, value=10)
    gen_clicked = st.sidebar.button("Generate prompts from topic")
    if gen_clicked and openai_key and topic_input:
        with st.spinner("Generating prompts…"):
            prompts_list, keywords_list_from_gen, err = generate_prompts_from_topic(
                topic_input,
                api_key=openai_key,
                count=gen_count,
                default_country=country or "us",
            )
        if err:
            st.sidebar.error(err)
        else:
            path = save_prompts_to_file(
                prompts_list, topic_input, tracking_keywords=keywords_list_from_gen
            )
            st.session_state.generated_prompts = prompts_list
            st.session_state.generated_keywords = keywords_list_from_gen or None
            st.sidebar.success(
                f"Saved {len(prompts_list)} prompts and {len(keywords_list_from_gen or [])} keywords to **{path.name}**"
            )

    run_generated_clicked = st.sidebar.button("Run bulk with generated prompts") if st.session_state.generated_prompts else False

    st.sidebar.divider()

    # Bulk run
    if (bulk_clicked or simulate_clicked or run_generated_clicked) and api_token:
        prompts_to_run = []
        if run_generated_clicked and st.session_state.generated_prompts:
            prompts_to_run = st.session_state.generated_prompts
        elif simulate_clicked:
            demo_path = Path("prompts/demo-prompts.json")
            if demo_path.exists():
                with open(demo_path, encoding="utf-8") as f:
                    prompts_to_run = json.load(f)
            else:
                prompts_to_run = [
                    {"prompt": default_prompt, "country": country or "us"},
                ]
        elif bulk_file:
            try:
                prompts_to_run = json.load(bulk_file)
                if not isinstance(prompts_to_run, list):
                    prompts_to_run = [prompts_to_run]
            except Exception as e:
                st.error(f"Invalid JSON: {e}")
                prompts_to_run = []
        if prompts_to_run:
            # Use generated keywords when running from generated prompts, else sidebar keywords
            bulk_keywords = (
                st.session_state.generated_keywords
                if run_generated_clicked and st.session_state.get("generated_keywords")
                else keywords_list
            )
            with st.status("Running bulk prompts…", expanded=True) as status:
                progress_bar = st.progress(0, text="Starting…")
                current_prompt_placeholder = st.empty()

                def on_progress(current: int, total: int, prompt_text: str):
                    progress_bar.progress(current / total if total else 0, text=f"Prompt {current}/{total}")
                    preview = (prompt_text[:55] + "…") if len(prompt_text) > 55 else prompt_text
                    current_prompt_placeholder.caption(f"**Current:** {preview}")

                run_id, _ = run_bulk(
                    prompts_to_run,
                    selected_models or list(LLM_ORDER),
                    country,
                    api_token,
                    tracking_keywords=bulk_keywords,
                    on_progress=on_progress,
                )
                progress_bar.progress(1.0, text="Done")
                current_prompt_placeholder.caption("")
                status.update(label=f"Bulk run saved: runs/{run_id}", state="complete")
            st.success(f"Saved to `runs/{run_id}`")
            # Load the bulk run so we can view results per prompt
            run_path = RUNS_DIR / run_id
            if run_path.exists():
                meta_file = run_path / "run-metadata.json"
                if meta_file.exists():
                    with open(meta_file, encoding="utf-8") as f:
                        bulk_meta = json.load(f)
                    loaded = load_run_from_dir(run_path, prompt_index=0)
                    if loaded:
                        st.session_state.results = loaded["results"]
                        st.session_state.parsed = loaded["parsed"]
                        st.session_state.last_prompt = loaded["prompt"]
                        st.session_state.last_country = loaded["country"]
                        st.session_state.serp = loaded.get("serp")
                        st.session_state.keywords_used = (
                            loaded.get("tracking_keywords") or DEFAULT_TRACKING_KEYWORDS
                        )
                        st.session_state.analysis_text = loaded.get("analysis_text")
                        st.session_state.last_run_id = run_id
                        st.session_state.last_run_prompts = bulk_meta.get("prompts") or []
                        st.session_state.selected_prompt_index = 0

    # Single run — with per-model progress
    if run_clicked and api_token and selected_models:
        st.subheader("Run progress")
        # One status line per model; updated on phase and completion
        placeholders = {}
        for key in selected_models:
            name = LLM_SCRAPERS.get(key, {}).get("name", key)
            placeholders[key] = st.empty()
            placeholders[key].info(f"⏳ **{name}** — Calling API…")

        def on_phase(model_key: str, phase: str, detail: str):
            name = LLM_SCRAPERS.get(model_key, {}).get("name", model_key)
            if phase == "triggering":
                placeholders[model_key].info(f"⏳ **{name}** — Triggering…")
            elif phase == "polling":
                placeholders[model_key].info(f"⏳ **{name}** — Polling for response…")

        def on_model_complete(model_key: str, result: LLMResult):
            name = result.model_name
            if result.status == "success":
                placeholders[model_key].success(f"✅ **{name}** — Complete")
            else:
                err = (result.error_message or result.status)[:80]
                placeholders[model_key].error(f"❌ **{name}** — {result.status}: {err}")

        results = run_all_llms_with_progress_sync(
            prompt,
            selected_models,
            country,
            api_token=api_token,
            on_model_complete=on_model_complete,
            on_phase=on_phase,
        )
        st.session_state.results = results
        st.session_state.last_prompt = prompt
        st.session_state.last_country = country
        st.session_state.keywords_used = keywords_list
        parsed = [parse_result(r, keywords_list) for r in results]
        st.session_state.parsed = parsed
        st.session_state.serp = None
        st.session_state.analysis_text = None
        run_id = save_single_run(
            results, parsed, prompt, country, serp=None,
            tracking_keywords=keywords_list,
        )
        st.session_state.last_run_id = run_id
        st.session_state.last_run_prompts = [prompt]  # single prompt, no selector
        st.session_state.selected_prompt_index = 0
        st.success(f"All models finished. Run saved to **runs/{run_id}**.")

    # SERP fetch (optional, after a run) — save to current run when available
    if st.session_state.results and api_token:
        if st.sidebar.button("Fetch SERP for this query"):
            q = st.session_state.last_prompt or prompt
            with st.spinner("Fetching Google SERP…"):
                serp_list = run_async(
                    fetch_serp(q, st.session_state.last_country or country, api_token=api_token)
                )
            st.session_state.serp = serp_list
            if st.session_state.last_run_id:
                save_serp_to_run(st.session_state.last_run_id, serp_list)

    # Main area: show results
    results = st.session_state.results
    parsed = st.session_state.parsed
    serp = st.session_state.serp
    kw = st.session_state.keywords_used

    # Show generated prompts and keywords when available
    if st.session_state.generated_prompts:
        st.subheader("Generated prompts")
        with st.expander("View generated prompts", expanded=True):
            prompt_rows = [
                {"#": i + 1, "Prompt": p.get("prompt", ""), "Country": p.get("country", "us")}
                for i, p in enumerate(st.session_state.generated_prompts)
            ]
            st.dataframe(prompt_rows, use_container_width=True, hide_index=True)
        if st.session_state.get("generated_keywords"):
            st.caption("**Tracking keywords for this run:**")
            st.write(", ".join(st.session_state.generated_keywords))
        st.divider()

    if results and parsed:
        # Per-prompt selector for multi-prompt (bulk) runs
        last_run_prompts = st.session_state.get("last_run_prompts") or []
        current_index = st.session_state.get("selected_prompt_index", 0)
        if len(last_run_prompts) > 1 and st.session_state.get("last_run_id"):
            run_id = st.session_state.last_run_id
            prompt_options = list(range(len(last_run_prompts)))
            labels = [
                f"{i + 1}. {(p[:48] + '…') if len(p) > 48 else p}"
                for i, p in enumerate(last_run_prompts)
            ]
            selected = st.selectbox(
                "View results for prompt",
                prompt_options,
                index=min(current_index, len(prompt_options) - 1),
                format_func=lambda i: labels[i],
                key="prompt_selector",
            )
            if selected != current_index:
                st.session_state.selected_prompt_index = selected
                run_path = RUNS_DIR / run_id
                reloaded = load_run_from_dir(run_path, prompt_index=selected)
                if reloaded:
                    st.session_state.results = reloaded["results"]
                    st.session_state.parsed = reloaded["parsed"]
                    st.session_state.last_prompt = reloaded["prompt"]
                    st.session_state.last_country = reloaded["country"]
                    st.session_state.serp = reloaded.get("serp")
                    st.session_state.analysis_text = reloaded.get("analysis_text")
                st.rerun()
            st.caption(f"Showing results for **{len(last_run_prompts)}** prompts in this run.")
            st.divider()

        # Show current query and search location
        loc = (st.session_state.get("last_country") or "").lower() or None
        loc_label = COUNTRY_DISPLAY.get(loc, loc.upper() if loc else "Default")
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"**Query:** {st.session_state.get('last_prompt') or '—'}")
        with col2:
            st.markdown(f"**Search location:** {loc_label}")
        st.divider()

        render_signals_table(parsed)
        st.divider()
        render_response_tabs(results, kw)
        st.divider()

        # SERP section
        with st.expander("Google SERP Results"):
            if serp:
                serp_rows = [{"Position": s.position, "Title": s.title, "URL": s.url, "Snippet": s.snippet} for s in serp]
                st.dataframe(serp_rows, use_container_width=True, hide_index=True)
            else:
                st.info("Click 'Fetch SERP for this query' in the sidebar to compare with Google results.")

        # Comparative analysis (OpenAI)
        st.subheader("Comparative analysis")
        openai_key = get_openai_api_key()
        if not openai_key:
            st.warning("Set **OPENAI_API_KEY** in your .env file to run LLM-based analysis of SERP and AI results.")
        else:
            if st.button("Run comparative analysis with OpenAI"):
                with st.spinner("Analyzing SERP and AI answers…"):
                    analysis = run_comparative_analysis(
                        st.session_state.last_prompt or "",
                        results,
                        serp,
                        api_key=openai_key,
                        tracking_keywords=kw,
                    )
                    st.session_state.analysis_text = analysis
                    if st.session_state.last_run_id:
                        save_analysis_to_run(st.session_state.last_run_id, analysis)
            if st.session_state.analysis_text:
                st.markdown(st.session_state.analysis_text)

        st.divider()

        # Export
        export_json = build_export_json(
            results, parsed, serp or None,
            st.session_state.last_prompt,
            st.session_state.last_country,
        )
        run_date = datetime.now().strftime("%Y-%m-%d")
        st.download_button(
            "Export run as JSON",
            data=export_json,
            file_name=f"run-{run_date}.json",
            mime="application/json",
        )
    else:
        st.info("Enter a prompt and click **Run Across All Models** to compare LLM responses.")


if __name__ == "__main__":
    main()
