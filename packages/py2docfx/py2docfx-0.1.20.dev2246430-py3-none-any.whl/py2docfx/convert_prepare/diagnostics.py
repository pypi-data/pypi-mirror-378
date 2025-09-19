# diagnostics.py (or inline with your existing helper module)

import os, re, json, textwrap
from pathlib import Path
from py2docfx import PACKAGE_ROOT
from py2docfx.docfx_yaml.logger import get_logger, run_async_subprocess

# Reuse your global install options if you like
pip_install_common_options = ["--no-compile", "--disable-pip-version-check", "-vvv"]

SECRET_PATTERN = re.compile(r"(//[^:/]+:)([^@]+)(@)")  # //user:pass@ → //user:****@

def _mask(s: str) -> str:
    if not s:
        return s
    return SECRET_PATTERN.sub(r"\1****\3", s)

def _env_var(name: str) -> str:
    val = os.environ.get(name)
    return f"{name}={_mask(val)}" if val else f"{name}="

async def pip_diag_bundle(
    exe_path: str,
    package_name: str,
    extra_install_options: list[str],
    report_dir: str = "pip_reports",
    include_metadata_peek: bool = True,
):
    """
    Collect a comprehensive diagnostic snapshot for pip in the current venv:
      - pip/python version
      - pip config (with origins)
      - pip debug (platform & tags)
      - env vars likely to affect pip
      - pip list (packages in the venv)
      - dry-run resolver report for the target package (JSON)
      - optional: METADATA/Requires-Dist peek for any downloaded wheel
    """
    logger = get_logger(__name__)
    out_dir = Path(PACKAGE_ROOT) / report_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    # 0) Write a quick "header" file with env context (sanitized)
    ctx = {
        "cwd": str(PACKAGE_ROOT),
        "PIP_INDEX_URL": os.environ.get("PIP_INDEX_URL"),
        "PIP_EXTRA_INDEX_URL": os.environ.get("PIP_EXTRA_INDEX_URL"),
        "HTTPS_PROXY": os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy"),
        "HTTP_PROXY": os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy"),
    }
    (out_dir / "00_env_context.txt").write_text(
        "\n".join(_env_var(k) for k in ctx.keys()), encoding="utf-8"
    )

    # 1) pip/python versions
    await run_async_subprocess(exe_path, ["-m", "pip", "--version"], logger, cwd=PACKAGE_ROOT)
    await run_async_subprocess(exe_path, ["-c", "import sys; import platform; print(sys.executable); print(sys.version); print(platform.platform())"], logger, cwd=PACKAGE_ROOT)

    # 2) Effective pip config
    await run_async_subprocess(exe_path, ["-m", "pip", "config", "list", "-v"], logger, cwd=PACKAGE_ROOT)  # [2](https://pip.pypa.io/en/stable/topics/configuration.html)

    # 3) Platform & wheel tag info
    await run_async_subprocess(exe_path, ["-m", "pip", "debug"], logger, cwd=PACKAGE_ROOT)  # [3](https://pip.pypa.io/en/stable/cli/pip_debug/)

    # 4) Snapshot venv packages (if any)
    await run_async_subprocess(exe_path, ["-m", "pip", "list", "--format=freeze"], logger, cwd=PACKAGE_ROOT)

    # 5) Resolver dry run with JSON report (no env changes)
    report_path = out_dir / f"{package_name.replace('==', '-').replace(' ', '_')}.dryrun.report.json"
    dry_run_cmd = (
        ["-m", "pip", "install", "--dry-run", "--ignore-installed", "--report", str(report_path)]
        + pip_install_common_options
        + extra_install_options
        + [package_name]
    )
    await run_async_subprocess(exe_path, dry_run_cmd, logger, cwd=PACKAGE_ROOT)  # [1](https://pip.pypa.io/en/stable/cli/pip_install/)

    # 6) Optional: peek at any already-downloaded wheel METADATA for quick "Requires-Dist" visibility
    if include_metadata_peek:
        try:
            import zipfile, glob
            wheel_candidates = glob.glob("**/*.whl", recursive=True)
            wheel_candidates = [w for w in wheel_candidates if "microsoft_teams_ai-2.0.0a1-" in w or "microsoft-teams-ai-2.0.0a1-" in w]
            if wheel_candidates:
                wheel_candidates.sort()
                whl = wheel_candidates[-1]
                with zipfile.ZipFile(whl) as zf:
                    meta_name = [n for n in zf.namelist() if n.endswith(".dist-info/METADATA")][0]
                    meta_text = zf.read(meta_name).decode("utf-8", "replace")
                    (out_dir / "wheel_METADATA.txt").write_text(meta_text, encoding="utf-8")
        except Exception as _:
            # Non-fatal
            pass

    logger.info(f"[pip-diag] Wrote diagnostic bundle to: {out_dir}")