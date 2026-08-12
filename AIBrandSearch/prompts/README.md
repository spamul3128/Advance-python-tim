# Prompt lists for bulk run

Upload one of these JSON files in the app sidebar under **Bulk run** → **Upload prompt list (JSON)**, then click **Run Bulk**.

## Format

A JSON **array** of objects. Each object can have:

| Field     | Required | Description |
|----------|----------|-------------|
| `prompt` | Yes      | The search query to send to each LLM. |
| `country`| No       | Geo for the request (e.g. `"us"`, `"uk"`, `"de"`, `"fr"`). If omitted, the app uses the country selected in the sidebar. |

## Example

```json
[
  { "prompt": "What tools monitor search results in LLMs?", "country": "us" },
  { "prompt": "Best CRM for startups", "country": "uk" },
  { "prompt": "Top proxy providers" }
]
```

## Files

- **demo-prompts.json** — Short 3-prompt demo.
- **batch-prompts.json** — Larger set (~20 prompts) for brand/SEO/visibility-style queries; duplicate and edit to build your own batch.
