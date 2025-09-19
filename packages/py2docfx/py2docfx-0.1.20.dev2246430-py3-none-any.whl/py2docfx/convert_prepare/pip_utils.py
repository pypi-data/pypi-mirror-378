import os
import sys
from pathlib import Path

from py2docfx import PACKAGE_ROOT
from py2docfx.docfx_yaml.logger import get_logger, run_async_subprocess, run_async_subprocess_without_executable

# NEW: diagnostics import
try:
    from diagnostics import pip_diag_bundle
except Exception:
    pip_diag_bundle = None  # tolerate missing diagnostics in non-CI runs

PYPI = "pypi"

# Keep your original common options; build commands as lists (no .split())
pip_install_common_options = [
    "--no-compile",
    "--disable-pip-version-check",
    "-vvv",
]

# --- NEW: helpers -------------------------------------------------------------

def _diag_enabled() -> bool:
    # Enable by default in CI; allow opt-out with PY2DOCFX_PIP_DIAG=0
    v = os.environ.get("PY2DOCFX_PIP_DIAG", "1").strip()
    return v not in ("0", "false", "False", "")

def _report_dir() -> str:
    return os.environ.get("PY2DOCFX_PIP_REPORT_DIR", "pip_reports")

def build_index_options(
    index_url: str | None = None,
    extra_index_urls: list[str] | None = None,
    trusted_hosts: list[str] | None = None,
    constraints_file: str | None = None,
) -> list[str]:
    """
    Build pip CLI options for index and constraints.
    Use this from call sites to pass consistent resolution settings.
    """
    opts: list[str] = []
    if index_url:
        opts += ["--index-url", index_url]
    if extra_index_urls:
        for u in extra_index_urls:
            if u:
                opts += ["--extra-index-url", u]
    if trusted_hosts:
        for h in trusted_hosts:
            if h:
                opts += ["--trusted-host", h]
    if constraints_file:
        opts += ["-c", constraints_file]
    return opts

# --- Existing functions with improvements ------------------------------------

async def download(package_name, path, extra_index_url=None, prefer_source_distribution=True):
    """
    Downloads a package from PyPI (or other index) to the specified path using pip.
    """
    download_param = ["pip", "download", "--dest", path, "--no-deps", package_name]
    if extra_index_url:
        # Note: For multiple mirrors use build_index_options and pass through install() signatures instead.
        download_param.extend(["--extra-index-url", extra_index_url])
    if prefer_source_distribution:
        download_param.append("--no-binary=:all:")
    else:
        download_param.append("--prefer-binary")

    py2docfx_logger = get_logger(__name__)
    await run_async_subprocess_without_executable(download_param, py2docfx_logger, cwd=PACKAGE_ROOT)


async def install(package_name, options):
    """
    Installs a package using the *current* Python (no explicit exe).
    Retains the original signature; enable diagnostics via env var.
    """
    py2docfx_logger = get_logger(__name__)

    # --- NEW: preflight diagnostics
    if _diag_enabled() and pip_diag_bundle is not None:
        try:
            await pip_diag_bundle(
                sys.executable,
                package_name,
                options,
                report_dir=_report_dir(),
            )
        except Exception as _:
            # Non-fatal: we still attempt the real install
            pass

    # Build the actual pip command (as list)
    install_cmd = ["pip", "install"] + pip_install_common_options + options + [package_name]
    try:
        await run_async_subprocess_without_executable(install_cmd, py2docfx_logger, cwd=PACKAGE_ROOT)
    except Exception:
        # --- NEW: after-failure diagnostics
        if _diag_enabled() and pip_diag_bundle is not None:
            try:
                await pip_diag_bundle(
                    sys.executable,
                    package_name,
                    options,
                    report_dir=os.path.join(_report_dir(), "after_failure"),
                )
            except Exception:
                pass
        raise


async def install_in_exe(exe_path, package_name, options):
    """
    Installs a package using the *given* Python executable path.
    FIX: don't duplicate exe_path in argv; pass "-m pip ..." only.
    """
    py2docfx_logger = get_logger(__name__)

    # --- NEW: preflight diagnostics
    if _diag_enabled() and pip_diag_bundle is not None:
        try:
            await pip_diag_bundle(
                exe_path,
                package_name,
                options,
                report_dir=_report_dir(),
            )
        except Exception:
            pass

    # Correct pip invocation: exe_path runs, args start with -m pip
    pip_cmd = ["-m", "pip", "install"] + pip_install_common_options + options + [package_name]
    try:
        await run_async_subprocess(exe_path, pip_cmd, py2docfx_logger, cwd=PACKAGE_ROOT)
    except Exception:
        # --- NEW: after-failure diagnostics
        if _diag_enabled() and pip_diag_bundle is not None:
            try:
                await pip_diag_bundle(
                    exe_path,
                    package_name,
                    options,
                    report_dir=os.path.join(_report_dir(), "after_failure"),
                )
            except Exception:
                pass
        raise


async def install_in_exe_async(exe_path, package_name, options):
    """
    Keeps the original async install; now includes diagnostics.
    """
    py2docfx_logger = get_logger(__name__)

    # --- NEW: preflight diagnostics
    if _diag_enabled() and pip_diag_bundle is not None:
        try:
            await pip_diag_bundle(
                exe_path,
                package_name,
                options,
                report_dir=_report_dir(),
            )
        except Exception:
            pass

    pip_cmd = ["-m", "pip", "install"] + pip_install_common_options + options + [package_name]
    try:
        await run_async_subprocess(exe_path, pip_cmd, py2docfx_logger, cwd=PACKAGE_ROOT)
    except Exception:
        # --- NEW: after-failure diagnostics
        if _diag_enabled() and pip_diag_bundle is not None:
            try:
                await pip_diag_bundle(
                    exe_path,
                    package_name,
                    options,
                    report_dir=os.path.join(_report_dir(), "after_failure"),
                )
            except Exception:
                pass
        raise