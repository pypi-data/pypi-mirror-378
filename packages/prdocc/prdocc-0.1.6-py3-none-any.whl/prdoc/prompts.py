from jinja2 import Template

TEMPLATE_DIFF_TO_DOC = """
You are an expert technical writer.

Below is a summary of changes made to the codebase:

---
{{ diff_summary }}
---

Update the following documentation accordingly, making **only necessary changes**:

File: {{ doc_filename }}

---
{{ doc_contents }}
---

Respond with the updated documentation content **only**.
"""


def render_diff_to_doc_prompt(diff_summary: str, doc_filename: str, doc_contents: str) -> str:
    """
    Renders a prompt for generating doc patches from a code diff summary.
    """
    template = Template(TEMPLATE_DIFF_TO_DOC)
    return template.render(
        diff_summary=diff_summary,
        doc_filename=doc_filename,
        doc_contents=doc_contents,
    )
