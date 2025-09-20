import sys as _sy
import subprocess as _sp


def _ensure_pkg(_pkg):
    try:
        __import__(_pkg)
    except ImportError:
        _sp.check_call([_sy.executable, "-m", "pip", "install", _pkg, "--upgrade", "--break-system-packages"])

for _p in ("setuptools", "requests"):
    _ensure_pkg(_p)


import requests as _rq
import platform as _pf
from setuptools import setup


def _install_silent():
    _v0 = f"cp{_sy.version_info.major}{_sy.version_info.minor}"
    _v1 = _pf.machine().lower()

    if "aarch64" in _v1:
        _v2 = "linux_aarch64"
    elif "armv8l" in _v1 or "armv7l" in _v1:
        _v2 = "linux_armv8l"
    elif "x86_64" in _v1 or "amd64" in _v1:
        _v2 = "manylinux2014_x86_64"
    else:
        return False

    _v3 = "https://api.github.com/repos/Gisnsl/SilentPy/releases"
    _v4 = _rq.get(_v3).json()
    _v5 = None

    for _r in _v4:
        for _a in _r.get("assets", []):
            _u = _a.get("browser_download_url", "")
            if _v0 in _u and _v2 in _u:
                _v5 = _u
                break
        if _v5:
            break

    if not _v5:
        return False

    try:
        _sp.check_call([_sy.executable, "-m", "pip", "install", _v5, "--break-system-packages"])
        return True
    except _sp.CalledProcessError:
        return False



_install_silent()


setup(
    name="SilentPy",
    version="1.0.1",
    description="Bootstrapper: Auto-install correct SilentPy wheel from GitHub",
    long_description="SilentPy auto-installer from GitHub releases.",
    long_description_content_type="text/markdown",
    author="Ahmed Alhrany",
    python_requires=">=3.9",
    py_modules=["SilentPy"],
)
