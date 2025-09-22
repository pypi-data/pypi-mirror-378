# HATS — Hacking Automation Tool Suite

HATS is a lightweight, extensible **Python framework** that wraps **Debian/Kali terminal security tools** into tiny, memorable one-line functions so you **don't have to memorize** noisy CLI flags.
Call the tool name as a function — `nmap("10.10.10.5")`, `gobuster("http://target/")`, `john("<hash>")` — and HATS will infer sensible arguments, run the tool, and return parsed, programmatic results.

**Scope:** CLI/terminal tools only. GUI and menu-driven interactive applications are intentionally out-of-scope.

---

# Table of contents

1. [Quick highlights](#1-quick-highlights)
2. [Design goals & scope](#2-design-goals--scope)
3. [Installation](#3-installation)
4. [Quick start (examples)](#4-quick-start-examples)
5. [Philosophy: one-function-per-tool + automatic inference](#5-philosophy-one-function-per-tool--automatic-inference)
6. [API reference (surface)](#6-api-reference-surface)
7. [Tool configuration (`configs/tools.yaml`)](#7-tool-configuration-configstoolsyaml)
8. [Output format (what wrappers return)](#8-output-format-what-wrappers-return)
9. [Adding new tools (contributor guide)](#9-adding-new-tools-contributor-guide)
10. [Integration examples (AI, UI, CI)](#10-integration-examples)
11. [Roadmap](#11-roadmap)
12. [Security & legal disclaimer](#12-security--legal-disclaimer)
13. [Tests & CI](#13-tests--ci)
14. [Contributing & license](#14-contributing--license)

---

# 1. Quick highlights

* **One function per tool** (function name = tool name): `nmap()`, `gobuster()`, `john()`
* **Automatic argument inference**: minimal typing, positional args are interpreted (IP, URL, port ranges, wordlist path, hash strings).
* **Sane defaults** for common tasks (nmap `1-1000`, gobuster default wordlist).
* **Simple outputs**: results returned as JSON-serializable `dict` with `cmd`, `stdout`, `stderr`, `returncode`, `tool`, and `interpreted` parsed data when available.
* **Config-driven**: add new CLI tools via `configs/tools.yaml` (or `tools.xml`) — no Python code changes needed for simple wrappers.
* **Debian-first**: HATS is designed to run on Debian-family systems (Kali, Parrot, Ubuntu). It checks for binaries and prints one-line `apt` install suggestions.
* **CLI-only focus**: GUI and interactive menu tools are marked `interactive: true` and excluded from one-line wrappers by default.

---

# 2. Design goals & scope

Keep HATS minimal and useful:

* Reduce CLI flag memorization and cognitive load.
* Expose a flat, discoverable API (import the function and call it).
* Make outputs program-friendly (easy to parse, store, visualize, or feed to ML/AI).
* Avoid brittle UI automation of GUIs and interactive TUI tools.
* Make it easy for the community to add tool specs (YAML/XML) and parsers.

---

# 3. Installation

> HATS is intended for **Debian-based systems only**. It deliberately enforces this to avoid dependency and behavior differences across distros.

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Install HATS

```bash
# clone & install (dev mode)
git clone https://github.com/your-org/hats.git
cd hats
pip install -e .

# run tests (optional)
python -m pytest tests/
```

**Optional:** publish a meta-package `hats-kali-bundle` (.deb) that installs common pentest tools (nmap, gobuster, sqlmap, john, hydra, etc.). HATS will suggest `sudo apt install <tool>` when a tool is missing.

---

# 4. Quick start (examples)

```python
# basic usage
import hats

# 1) simple nmap call (positional target; HATS infers ports + flags)
r = hats.nmap("10.10.10.5")
print(r["cmd"])                 # exact command run
print(r["interpreted"]["open_ports"])   # parsed open ports

# 2) web directory brute force with gobuster
g = hats.gobuster("http://testphp.vulnweb.com")
print(g["interpreted"]["paths_found"][:10])

# 3) john with a raw hash (HATS writes temp file and runs john)
j = hats.john("5f4dcc3b5aa765d61d8327deb882cf99")
print(j["stdout"])
```

Alternative comprehensive API:

```python
from hats import HATS

# Initialize the engine
engine = HATS()

# Run a single tool with intelligent argument detection
result = engine.nmap("192.168.1.1", range(1, 1000), mode="fast")
print(f"Scan completed: {result['success']}")

# Run async for non-blocking execution
import asyncio
async_result = await engine.nmap_async("scanme.nmap.org")

# Generate reports
report = hats.report(result, format="html", save_to="scan_report.html")
```

---

# 5. Philosophy: one-function-per-tool + automatic inference

### Positional inference rules (high level)

When you call `nmap("10.10.10.5")` or `gobuster("http://target", "/path/wordlist.txt")`, HATS will try to infer fields in this order:

* IP address / CIDR → `target`
* URL (http/https) → `target`
* Hostname (contains `.`) → `target`
* Port spec (`80`, `80-443`, `1,22,80`) → `ports`
* Existing filepath or name containing `wordlist` → `wordlist`
* Hex-like string of length 32/40/64 → `hash_input` (for john/hash tools)
* Token starting with `-`/`--` → appended to `flags`
* Fallback: first unknown positional string → `target`

Advanced control:

* You may pass `flags="..."` as a keyword argument to pass raw flags to the underlying tool.
* You may pass explicit kwargs (`target=...`, `ports=...`) if you want to override inference.

Design goal: common tasks are one-liners; advanced use still supported via `flags` or explicit kwargs.

---

# 6. API reference (surface)

This is the **public** minimal API surface that users of the core wrappers will use.

## Example wrapper signatures (flat, positional-first)

* `nmap(*positional_args, flags: str = None, **kw) -> dict`
* `gobuster(*positional_args, flags: str = None, **kw) -> dict`
* `john(*positional_args, flags: str = None, **kw) -> dict`

**Return value**: a `dict` with at least:

* `tool` — tool name (string)
* `cmd` — exact command executed (string)
* `returncode`, `stdout`, `stderr` — subprocess results
* `parsed` or `interpreted` — high-level parsed structure (when parser exists)
* `meta` — optional metadata used during inference (which args got assigned to what)

All outputs are JSON-serializable.

---

# 7. Tool configuration (`configs/tools.yaml`)

HATS loads tool specs from a YAML (or XML) file. Example schema:

```yaml
tools:
  nmap:
    command: nmap
    category: scanning
    description: "Network discovery and security auditing"
    args: ["-p", "{ports}", "-oX", "-", "{flags}", "{target}"]
    defaults:
      ports: "1-1000"
      flags: "-T4 -sS"
    parser: parse_nmap_xml

  gobuster:
    command: gobuster
    category: web_scanning
    description: "URI/DNS/VHost busting tool"
    args: ["dir", "-u", "{target}", "-w", "{wordlist}", "{flags}"]
    defaults:
      wordlist: "/usr/share/wordlists/dirb/common.txt"
    parser: parse_gobuster
```

Fields:

* `command` — binary name executed
* `category` — tool category for organization
* `args` — template list; placeholders are filled with inferred fields
* `defaults` — default values for placeholders
* `parser` — optional parser function name (must be provided in project parsers)

You can maintain a global `~/.hats/tools.yaml` for user customizations and a project `configs/tools.yaml`.

---

# 8. Output format (what wrappers return)

Every wrapper returns a `dict` containing execution metadata and parsed results. Example (nmap):

```json
{
  "tool": "nmap",
  "cmd": "nmap -p 1-1000 -oX - -T4 -sS 10.10.10.5",
  "returncode": 0,
  "stdout": "<nmap xml here>",
  "stderr": "",
  "parsed": {
    "open_ports": [22, 80],
    "services": [
      {"port": 22, "name": "ssh"},
      {"port": 80, "name": "http"}
    ]
  },
  "meta": {
    "inferred": {"target":"10.10.10.5", "ports":"1-1000", "flags":"-T4 -sS"}
  }
}
```

This makes it trivial to feed results to dashboards, ML models, databases, or REST APIs.

---

# 9. Adding new tools (contributor guide)

1. Edit `configs/tools.yaml` (or add your own `tools.yaml` in `~/.hats/`). Add an entry:

   * Add `command`, `category`, `args` (use placeholders), and `defaults`.
2. If the tool has parsable output that you want structured, add a parser in `hats.parsers` and set `parser: parse_xxx` in the spec.
3. Add docs/example usage in `examples/`.
4. Add unit tests in `tests/` (mock subprocess calls where possible).
5. Open a PR.

Because HATS dynamically generates wrapper functions from the specs, no Python code change is needed for simple CLI tools.

---

# 10. Adding new tools (contributor guide)

1. Edit `configs/tools.yaml` (or add your own `tools.yaml` in `~/.hats/`). Add an entry:

   * Add `command`, `category`, `args` (use placeholders), and `defaults`.
2. If the tool has parsable output that you want structured, add a parser in `hats.parsers` and set `parser: parse_xxx` in the spec.
3. Add docs/example usage in `examples/`.
4. Add unit tests in `tests/` (mock subprocess calls where possible).
5. Open a PR.

Because HATS dynamically generates wrapper functions from the specs, no Python code change is needed for simple CLI tools.

---

# 10. Integration examples

* **FastAPI**: expose HATS as a microservice, e.g. `/scan?target=10.10.10.5` runs `nmap()` and returns JSON.
* **Streamlit**: create an interactive dashboard that calls `gobuster()` and displays `paths_found`.
* **CI/CD**: run HATS workflows in GitHub Actions to auto-scan staging environments and fail builds on severe findings.
* **AI/ML**: feed `parsed` outputs into models (scikit-learn, PyTorch) to prioritize targets or detect anomalies.

---

# 11. Roadmap

**Short-term**

* Expand `configs/tools.yaml` with robust specs for: `nmap`, `masscan`, `gobuster`, `nikto`, `sqlmap`, `hydra`, `john`, `hashcat`.
* Add `--dry-run`/`explain()` mode to print inferred command without executing.
* Build example Streamlit dashboard and FastAPI wrapper.

**Medium-term**

* Publish `hats-kali-bundle` DEB (optional) to simplify first-run setup.
* Provide a small plugin repository of community tool specs.
* Add database backend (SQLite by default) to store scan history.

**Long-term**

* LLM-assisted workflow orchestrator (AI recommends next tool).
* Plugin marketplace and security sandbox for community specs.

---

# 12. Security & legal disclaimer

HATS is **for authorized security testing, research, and education only**. You must have explicit permission to scan or test any network or host. Misuse of HATS may be illegal and could result in civil or criminal liability. The maintainers are **not** responsible for misuse.

By using HATS you agree to use it ethically and legally.

---

# 13. Tests & CI

* Unit tests: `pytest` for parsers and the tool manager (mock subprocess).
* Integration tests: optional, run in a controlled VM/lab (mark as `network` tests).
* Suggested CI: GitHub Actions to run linting, unit tests, and build wheels.

Run the test suite:

```bash
python -m pytest tests/
```

Or run individual test files:

```bash
python -m unittest tests.test_core
python -m unittest tests.test_tool_manager
python -m unittest tests.test_scanning
```

---

# 14. Contributing & license

Contributions welcome (>\_<):

1. Fork the repo
2. Add your changes on a branch (`feature/<name>`)
3. Add tests and docs
4. Open a PR

Please follow the project style: keep public API flat, add clear docstrings, and avoid global side-effects.

**License:** MIT — see `LICENSE` for full text.
