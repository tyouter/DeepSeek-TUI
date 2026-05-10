#!/usr/bin/env python3
"""
DeepSeek TUI — Gate Runner (v2.0)
Usage:  python scripts/check.py [quick|full|pre-push]
  quick    — fmt + cargo check (fast, for pre-commit)
  full     — fmt + check + build + clippy + test (for comprehensive check)
  pre-push — same as full, for pre-push hook

Exits with code 0 on success, 1 on any failure.
"""
import subprocess
import sys
import shutil
import platform
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def run_step(name: str, cmd: list[str]) -> bool:
    desc = " ".join(cmd)
    print(f"  [{name}] {desc} ...", end=" ", flush=True)
    result = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    if result.returncode == 0:
        print("PASSED")
        return True
    else:
        print("FAILED")
        if result.stderr:
            # Show first 3 relevant error lines
            lines = [l for l in result.stderr.strip().split("\n") if "error" in l.lower() or "warning" in l.lower()]
            if not lines:
                lines = result.stderr.strip().split("\n")[-5:]
            for line in lines[:5]:
                print(f"    {line}")
        return False


def check_tool(name: str) -> bool:
    if shutil.which(name):
        return True
    print(f"  ERROR: '{name}' not found on PATH")
    return False


def check_platform_toolchain() -> bool:
    """Check platform-specific toolchain requirements."""
    system = platform.system()
    ok = True

    if system == "Windows":
        # Check for MSVC linker or GNU toolchain
        has_link = shutil.which("link.exe")
        has_gcc = shutil.which("gcc")
        has_clang = shutil.which("clang")
        if not (has_link or has_gcc or has_clang):
            print("  [platform] WARNING: No C linker found (link.exe / gcc / clang)")
            print("    Install 'Build Tools for Visual Studio' with C++ workload,")
            print("    or install MinGW/MSYS2 for the GNU toolchain.")
            print("    https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022")
            # Don't fail yet — cargo check doesn't need a linker
        else:
            linker = "link.exe" if has_link else ("gcc" if has_gcc else "clang")
            print(f"  [platform] C linker found: {linker}")
    elif system == "Linux":
        has_cc = shutil.which("cc") or shutil.which("gcc")
        if not has_cc:
            print("  [platform] WARNING: No C compiler found. Install build-essential or equivalent.")
            ok = False
    elif system == "Darwin":
        has_xcode = shutil.which("xcrun")
        if not has_xcode:
            print("  [platform] WARNING: Xcode command line tools may not be installed.")
            print("    Run: xcode-select --install")

    print(f"  [platform] Detected: {system} ({platform.machine()})")
    return ok


def main():
    mode = (sys.argv[1] if len(sys.argv) > 1 else "quick").lower()
    if mode not in ("quick", "full", "pre-push"):
        print(f"Usage: python scripts/check.py [quick|full|pre-push]")
        sys.exit(1)

    # Map 'pre-push' to 'full'
    if mode == "pre-push":
        mode = "full"

    print(f"{'=' * 44}")
    print(f"  DeepSeek TUI Gate Check — {mode}")
    print(f"{'=' * 44}")
    print()

    if not check_tool("cargo"):
        sys.exit(1)

    # Platform pre-check
    check_platform_toolchain()

    # ─── Steps ───
    steps: list[tuple[str, list[str]]] = [
        ("fmt", ["cargo", "fmt", "--all", "--", "--check"]),
        ("check", ["cargo", "check", "--workspace", "--all-targets"]),
    ]

    if mode == "full":
        steps += [
            ("build", ["cargo", "build", "--workspace"]),
            ("clippy", ["cargo", "clippy", "--workspace", "--all-targets", "--all-features", "--", "-D", "warnings"]),
            ("test", ["cargo", "test", "--workspace", "--all-features"]),
            # Check for dependency advisories (informational — don't fail)
            ("audit", ["cargo", "audit", "--deny", "warnings"] if shutil.which("cargo-audit") else None),
        ]

    failed = 0
    for name, cmd in steps:
        if cmd is None:
            print(f"  [{name}] SKIPPED (tool not installed)")
            continue
        if not run_step(name, cmd):
            failed += 1

    print()
    print(f"{'=' * 44}")
    if failed:
        print(f"  FAILED: {failed} gate(s) failed. Fix before proceeding.")
        sys.exit(1)
    else:
        print(f"  All gates passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
