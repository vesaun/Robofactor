# Robofactor
A GitHub/GitLab app that scans your repo daily, finds low-risk code smells, and opens tiny PRs (each focused on one fix) with tests or checks included. Think: a polite junior dev who only touches what’s safe and merges fast.

uv venv .venv
Activate it:
macOS/Linux:
source .venv/bin/activate

uv pip install -e '.[dev]'
