#!/usr/bin/env python3
"""
EqualTales QA Agent
===================
Continuous monitoring and quality assurance for the EqualTales project.

This script runs all quality checks and provides a comprehensive report.
Use as a pre-commit hook, in CI/CD, or for manual verification.

Usage:
    python scripts/qa_agent.py              # Run all checks
    python scripts/qa_agent.py --quick      # Quick checks only (no coverage)
    python scripts/qa_agent.py --watch      # Watch mode (re-run on file changes)
    python scripts/qa_agent.py --fix        # Attempt to fix issues automatically
"""

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
MCP_SERVER_DIR = PROJECT_ROOT / "mcp_server"
DATA_DIR = PROJECT_ROOT / "data"

# Minimum coverage thresholds
MIN_BACKEND_COVERAGE = 70
MIN_FRONTEND_COVERAGE = 70

# File patterns to check
PYTHON_FILES = ["backend/**/*.py", "mcp_server/**/*.py", "scripts/**/*.py"]
JS_FILES = ["frontend/src/**/*.js", "frontend/src/**/*.jsx"]


# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class CheckResult:
    """Result of a single QA check."""
    name: str
    passed: bool
    message: str
    duration: float = 0.0
    details: Optional[str] = None
    can_fix: bool = False


@dataclass
class QAReport:
    """Complete QA report."""
    timestamp: str
    checks: list = field(default_factory=list)
    total_duration: float = 0.0

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks)

    @property
    def summary(self) -> str:
        passed = sum(1 for c in self.checks if c.passed)
        total = len(self.checks)
        return f"{passed}/{total} checks passed"


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def run_command(cmd: list, cwd: Path = None, timeout: int = 300) -> tuple:
    """Run a command and return (success, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", f"Command timed out after {timeout}s"
    except FileNotFoundError:
        return False, "", f"Command not found: {cmd[0]}"


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def print_check(result: CheckResult):
    """Print a check result."""
    icon = "✅" if result.passed else "❌"
    print(f"{icon} {result.name}: {result.message} ({result.duration:.1f}s)")
    if result.details and not result.passed:
        for line in result.details.split("\n")[:10]:
            print(f"   {line}")
        if len(result.details.split("\n")) > 10:
            print(f"   ... (truncated)")


# ============================================================
# QA CHECKS
# ============================================================

def check_knowledge_base() -> CheckResult:
    """Validate the knowledge base structure and data."""
    start = time.time()
    kb_path = DATA_DIR / "women_knowledge_base.json"

    if not kb_path.exists():
        return CheckResult(
            name="Knowledge Base",
            passed=False,
            message="File not found",
            duration=time.time() - start,
        )

    try:
        with open(kb_path) as f:
            kb = json.load(f)

        issues = []

        # Check structure
        if "women" not in kb:
            issues.append("Missing 'women' key")
        if "stereotype_categories" not in kb:
            issues.append("Missing 'stereotype_categories' key")

        # Check women entries
        women = kb.get("women", [])
        if len(women) < 50:
            issues.append(f"Expected 50 women, found {len(women)}")

        required_woman_fields = ["name", "era", "achievement", "fairy_tale_moment", "age_adaptations", "counters_stereotypes"]
        for woman in women:
            for field in required_woman_fields:
                if field not in woman:
                    issues.append(f"Woman '{woman.get('name', 'unknown')}' missing '{field}'")

            # Check age_adaptations has all groups
            adaptations = woman.get("age_adaptations", {})
            for group in ["young", "middle", "older"]:
                if group not in adaptations:
                    issues.append(f"Woman '{woman.get('name')}' missing '{group}' adaptation")

        # Check categories
        categories = kb.get("stereotype_categories", {})
        if len(categories) < 14:
            issues.append(f"Expected 14 categories, found {len(categories)}")

        for cat_name, cat_data in categories.items():
            if "counter_message" not in cat_data:
                issues.append(f"Category '{cat_name}' missing 'counter_message'")
            if "suggested_women" not in cat_data:
                issues.append(f"Category '{cat_name}' missing 'suggested_women'")

        if issues:
            return CheckResult(
                name="Knowledge Base",
                passed=False,
                message=f"{len(issues)} validation errors",
                duration=time.time() - start,
                details="\n".join(issues[:10]),
            )

        return CheckResult(
            name="Knowledge Base",
            passed=True,
            message=f"{len(women)} women, {len(categories)} categories validated",
            duration=time.time() - start,
        )

    except json.JSONDecodeError as e:
        return CheckResult(
            name="Knowledge Base",
            passed=False,
            message="Invalid JSON",
            duration=time.time() - start,
            details=str(e),
        )


def check_python_syntax() -> CheckResult:
    """Check Python files for syntax errors."""
    start = time.time()
    errors = []

    python_files = list(BACKEND_DIR.glob("**/*.py")) + list(MCP_SERVER_DIR.glob("**/*.py"))

    for py_file in python_files:
        success, _, stderr = run_command(["python3", "-m", "py_compile", str(py_file)])
        if not success:
            errors.append(f"{py_file.name}: {stderr}")

    if errors:
        return CheckResult(
            name="Python Syntax",
            passed=False,
            message=f"{len(errors)} syntax errors",
            duration=time.time() - start,
            details="\n".join(errors),
        )

    return CheckResult(
        name="Python Syntax",
        passed=True,
        message=f"{len(python_files)} files OK",
        duration=time.time() - start,
    )


def check_backend_tests(coverage: bool = True) -> CheckResult:
    """Run backend pytest tests."""
    start = time.time()

    cmd = ["python3", "-m", "pytest", "tests/", "-v"]
    if coverage:
        cmd.extend(["--cov=.", "--cov-report=term-missing", f"--cov-fail-under={MIN_BACKEND_COVERAGE}"])

    success, stdout, stderr = run_command(cmd, cwd=BACKEND_DIR, timeout=180)

    if success:
        # Extract test count
        for line in stdout.split("\n"):
            if "passed" in line.lower():
                return CheckResult(
                    name="Backend Tests",
                    passed=True,
                    message=line.strip(),
                    duration=time.time() - start,
                )

        return CheckResult(
            name="Backend Tests",
            passed=True,
            message="All tests passed",
            duration=time.time() - start,
        )

    return CheckResult(
        name="Backend Tests",
        passed=False,
        message="Tests failed",
        duration=time.time() - start,
        details=stdout[-2000:] if stdout else stderr[-2000:],
    )


def check_frontend_tests(coverage: bool = True) -> CheckResult:
    """Run frontend Jest tests."""
    start = time.time()

    cmd = ["npm", "test", "--", "--watchAll=false", "--passWithNoTests"]
    if coverage:
        cmd.extend(["--coverage"])

    success, stdout, stderr = run_command(cmd, cwd=FRONTEND_DIR, timeout=180)

    if success:
        return CheckResult(
            name="Frontend Tests",
            passed=True,
            message="All tests passed",
            duration=time.time() - start,
        )

    return CheckResult(
        name="Frontend Tests",
        passed=False,
        message="Tests failed",
        duration=time.time() - start,
        details=stdout[-2000:] if stdout else stderr[-2000:],
    )


def check_frontend_build() -> CheckResult:
    """Check that frontend builds successfully."""
    start = time.time()

    success, stdout, stderr = run_command(
        ["npm", "run", "build"],
        cwd=FRONTEND_DIR,
        timeout=120,
    )

    if success:
        return CheckResult(
            name="Frontend Build",
            passed=True,
            message="Build successful",
            duration=time.time() - start,
        )

    return CheckResult(
        name="Frontend Build",
        passed=False,
        message="Build failed",
        duration=time.time() - start,
        details=stderr[-2000:] if stderr else stdout[-2000:],
    )


def check_env_file() -> CheckResult:
    """Check that .env file exists with required keys."""
    start = time.time()
    env_path = PROJECT_ROOT / ".env"

    if not env_path.exists():
        return CheckResult(
            name="Environment",
            passed=False,
            message=".env file not found",
            duration=time.time() - start,
            details="Create .env with OPENROUTER_API_KEY and OPENAI_API_KEY",
        )

    with open(env_path) as f:
        content = f.read()

    missing = []
    if "OPENROUTER_API_KEY" not in content:
        missing.append("OPENROUTER_API_KEY")
    if "OPENAI_API_KEY" not in content:
        missing.append("OPENAI_API_KEY")

    if missing:
        return CheckResult(
            name="Environment",
            passed=False,
            message=f"Missing keys: {', '.join(missing)}",
            duration=time.time() - start,
        )

    return CheckResult(
        name="Environment",
        passed=True,
        message="All required keys present",
        duration=time.time() - start,
    )


def check_dependencies() -> CheckResult:
    """Check that all dependencies are installed."""
    start = time.time()
    issues = []

    # Check Python dependencies
    requirements = BACKEND_DIR / "requirements.txt"
    if requirements.exists():
        success, _, stderr = run_command(
            ["python3", "-m", "pip", "check"],
            cwd=BACKEND_DIR,
        )
        if not success:
            issues.append(f"Python dependency issues: {stderr}")

    # Check Node dependencies
    node_modules = FRONTEND_DIR / "node_modules"
    if not node_modules.exists():
        issues.append("Frontend node_modules not found. Run: npm install")
    else:
        package_lock = FRONTEND_DIR / "package-lock.json"
        package_json = FRONTEND_DIR / "package.json"
        if package_json.exists() and package_lock.exists():
            if package_json.stat().st_mtime > package_lock.stat().st_mtime:
                issues.append("package.json newer than package-lock.json. Run: npm install")

    if issues:
        return CheckResult(
            name="Dependencies",
            passed=False,
            message=f"{len(issues)} issues found",
            duration=time.time() - start,
            details="\n".join(issues),
            can_fix=True,
        )

    return CheckResult(
        name="Dependencies",
        passed=True,
        message="All dependencies OK",
        duration=time.time() - start,
    )


def check_api_health() -> CheckResult:
    """Check if the backend API is responding (if running)."""
    start = time.time()

    try:
        import urllib.request
        req = urllib.request.Request("http://localhost:5001/api/health")
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read())
            if data.get("status") == "ok":
                return CheckResult(
                    name="API Health",
                    passed=True,
                    message=f"API running ({data.get('mode')} mode)",
                    duration=time.time() - start,
                )
    except Exception as e:
        return CheckResult(
            name="API Health",
            passed=True,  # Not a failure, just not running
            message="API not running (OK for tests)",
            duration=time.time() - start,
        )


def check_file_structure() -> CheckResult:
    """Check that required files and directories exist."""
    start = time.time()
    missing = []

    required = [
        PROJECT_ROOT / "backend" / "app.py",
        PROJECT_ROOT / "mcp_server" / "server.py",
        PROJECT_ROOT / "frontend" / "src" / "App.js",
        PROJECT_ROOT / "frontend" / "src" / "App.css",
        PROJECT_ROOT / "data" / "women_knowledge_base.json",
        PROJECT_ROOT / "CLAUDE.md",
    ]

    for path in required:
        if not path.exists():
            missing.append(str(path.relative_to(PROJECT_ROOT)))

    if missing:
        return CheckResult(
            name="File Structure",
            passed=False,
            message=f"{len(missing)} missing files",
            duration=time.time() - start,
            details="\n".join(missing),
        )

    return CheckResult(
        name="File Structure",
        passed=True,
        message="All required files present",
        duration=time.time() - start,
    )


# ============================================================
# QA AGENT
# ============================================================

class QAAgent:
    """Main QA agent that orchestrates all checks."""

    def __init__(self, quick: bool = False, fix: bool = False):
        self.quick = quick
        self.fix = fix
        self.report = QAReport(timestamp=datetime.now().isoformat())

    def run_check(self, check_fn, *args, **kwargs) -> CheckResult:
        """Run a check and add to report."""
        result = check_fn(*args, **kwargs)
        self.report.checks.append(result)
        print_check(result)
        return result

    def run_all_checks(self) -> QAReport:
        """Run all QA checks and return report."""
        start = time.time()

        print_header("EqualTales QA Agent")
        print(f"Mode: {'Quick' if self.quick else 'Full'}")
        print(f"Time: {self.report.timestamp}")

        # Structure checks
        print_header("Structure Checks")
        self.run_check(check_file_structure)
        self.run_check(check_env_file)
        self.run_check(check_dependencies)

        # Data checks
        print_header("Data Validation")
        self.run_check(check_knowledge_base)

        # Code checks
        print_header("Code Quality")
        self.run_check(check_python_syntax)

        # Test checks
        print_header("Test Suites")
        self.run_check(check_backend_tests, coverage=not self.quick)
        self.run_check(check_frontend_tests, coverage=not self.quick)

        # Build checks
        if not self.quick:
            print_header("Build Checks")
            self.run_check(check_frontend_build)

        # Runtime checks
        print_header("Runtime Checks")
        self.run_check(check_api_health)

        self.report.total_duration = time.time() - start

        # Summary
        print_header("Summary")
        print(f"Result: {self.report.summary}")
        print(f"Total time: {self.report.total_duration:.1f}s")

        if self.report.passed:
            print("\n🎉 All checks passed!")
        else:
            failed = [c for c in self.report.checks if not c.passed]
            print(f"\n⚠️  {len(failed)} check(s) failed:")
            for c in failed:
                print(f"   - {c.name}: {c.message}")

        return self.report

    def fix_issues(self):
        """Attempt to fix common issues."""
        print_header("Attempting Fixes")

        # Install dependencies
        print("Installing Python dependencies...")
        run_command(["python3", "-m", "pip", "install", "-r", "requirements.txt"], cwd=BACKEND_DIR)
        run_command(["python3", "-m", "pip", "install", "-r", "requirements-dev.txt"], cwd=BACKEND_DIR)

        print("Installing Node dependencies...")
        run_command(["npm", "install"], cwd=FRONTEND_DIR)

        print("✅ Dependency installation complete")


def watch_mode(qa: QAAgent, interval: int = 5):
    """Watch for file changes and re-run checks."""
    print_header("Watch Mode")
    print(f"Watching for changes every {interval}s...")
    print("Press Ctrl+C to stop\n")

    last_mtime = {}

    def get_file_mtimes():
        mtimes = {}
        for pattern in PYTHON_FILES + JS_FILES:
            for f in PROJECT_ROOT.glob(pattern):
                mtimes[str(f)] = f.stat().st_mtime
        return mtimes

    last_mtime = get_file_mtimes()

    try:
        while True:
            time.sleep(interval)
            current_mtime = get_file_mtimes()

            changed = []
            for f, mtime in current_mtime.items():
                if f not in last_mtime or last_mtime[f] != mtime:
                    changed.append(Path(f).name)

            if changed:
                print(f"\n📝 Changed: {', '.join(changed)}")
                qa.run_all_checks()

            last_mtime = current_mtime

    except KeyboardInterrupt:
        print("\n\nWatch mode stopped.")


# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="EqualTales QA Agent - Continuous quality monitoring"
    )
    parser.add_argument(
        "--quick", "-q",
        action="store_true",
        help="Quick mode: skip coverage and build checks",
    )
    parser.add_argument(
        "--watch", "-w",
        action="store_true",
        help="Watch mode: re-run on file changes",
    )
    parser.add_argument(
        "--fix", "-f",
        action="store_true",
        help="Attempt to fix common issues",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output report as JSON",
    )

    args = parser.parse_args()

    qa = QAAgent(quick=args.quick, fix=args.fix)

    if args.fix:
        qa.fix_issues()

    if args.watch:
        watch_mode(qa)
    else:
        report = qa.run_all_checks()

        if args.json:
            print("\n" + json.dumps({
                "timestamp": report.timestamp,
                "passed": report.passed,
                "summary": report.summary,
                "duration": report.total_duration,
                "checks": [
                    {
                        "name": c.name,
                        "passed": c.passed,
                        "message": c.message,
                        "duration": c.duration,
                    }
                    for c in report.checks
                ],
            }, indent=2))

        sys.exit(0 if report.passed else 1)


if __name__ == "__main__":
    main()
