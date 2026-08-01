"""Bundle HAYA AE ExtendScript into one launcher file with absolute paths."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from batch_deephouse.ae_config import AE_SCRIPTS_DIR, AE_WORK_ROOT, TEMPLATE_AEP

ACTIVE_SCRIPT = AE_WORK_ROOT / "_active_script.jsx"
COMMON_SCRIPT = AE_SCRIPTS_DIR / "ae_common.jsx"
SMOKE_PROJECT = AE_WORK_ROOT / "smoke_test.aep"


def _job_preamble(job: dict[str, Any] | None) -> str:
    """Inline job JSON so ExtendScript does not read external files."""
    lines = [f'var HAYA_WORK_DIR = "{AE_WORK_ROOT.resolve()}";']
    if job:
        lines.append("var HAYA_JOB = " + json.dumps(job, ensure_ascii=False) + ";")
    return "\n".join(lines) + "\n"


def write_active_script(
    body_script_name: str,
    *,
    job: dict[str, Any] | None = None,
) -> Path:
    """Write one self-contained JSX file for After Effects execution."""
    common_source = COMMON_SCRIPT.read_text(encoding="utf-8")
    template_path = str(TEMPLATE_AEP.resolve()).replace("\\", "\\\\")
    if "defaultTemplatePath" not in common_source:
        common_source += f'\nfunction defaultTemplatePath() {{ return "{template_path}"; }}\n'
    else:
        common_source = re.sub(
            r"function defaultTemplatePath\(\) \{[\s\S]*?\n\}",
            f'function defaultTemplatePath() {{ return "{template_path}"; }}',
            common_source,
            count=1,
        )

    body_source = (AE_SCRIPTS_DIR / body_script_name).read_text(encoding="utf-8")
    body_source = re.sub(r'#include\s+"ae_common\.jsx"\s*\n', "", body_source)
    bundled = (
        "#target aftereffects\n"
        + _job_preamble(job)
        + common_source
        + "\n"
        + body_source
    )
    AE_WORK_ROOT.mkdir(parents=True, exist_ok=True)
    ACTIVE_SCRIPT.write_text(bundled, encoding="utf-8")
    return ACTIVE_SCRIPT


def write_smoke_script() -> Path:
    """Write a minimal script that opens the template and saves a project."""
    project_path = str(SMOKE_PROJECT.resolve())
    body = f"""
runScript(function () {{
    var templateFile = new File(defaultTemplatePath());
    if (!templateFile.exists) {{
        throw new Error("Template missing: " + templateFile.fsName);
    }}
    app.open(templateFile);
    app.project.save(new File("{project_path}"));
    logLine("SMOKE SAVED: {project_path}");
}});
"""
    common_source = COMMON_SCRIPT.read_text(encoding="utf-8")
    common_source += (
        '\nfunction defaultTemplatePath() { return "'
        + str(TEMPLATE_AEP.resolve()).replace("\\", "\\\\")
        + '"; }\n'
    )
    bundled = "#target aftereffects\n" + common_source + body
    AE_WORK_ROOT.mkdir(parents=True, exist_ok=True)
    ACTIVE_SCRIPT.write_text(bundled, encoding="utf-8")
    return ACTIVE_SCRIPT
