# ☸ Kubernetes Health Checker — Built with Bazel

A beginner-friendly Kubernetes health check CLI built with **Bazel** and **Python**.
Checks your local cluster's nodes, pods, and namespaces in one command.

```bash
bazel run //:checker
```

```
  ☸  Kubernetes Health Check
  ───────────────────────────────────
  OK   Cluster is reachable

  Nodes:
  OK   Node: minikube  (Ready)

  Pods:
  OK   Pods — 7 running, 0 not running

  Namespaces:
  OK   Namespaces — 4 active, 0 terminating
```

---

## What is Bazel?

Bazel is an open-source **build and test tool** originally developed by Google.
It answers one question: **"how do I build this code correctly and fast — on any machine?"**

### The problem Bazel solves

When you write Python and share it with a teammate, things break:

- They have a different Python version
- They installed different package versions
- It works on your machine but not in CI

Bazel solves this with three core ideas:

**1. Hermetic builds**
Bazel downloads its own Python — it never uses whatever Python is installed on your machine.
The same code produces the same output on every machine, every time.

**2. Explicit dependency graph**
Every file must declare what it depends on. Nothing is implicit.
Bazel knows the full picture of what depends on what.

```
checker.py
    └── depends on → nodes.py
    └── depends on → pods.py
    └── depends on → namespaces.py
```

**3. Incremental builds and caching**
Bazel only rebuilds what actually changed.
If you edit `pods.py`, Bazel rebuilds `pods` and `checker` — but skips `nodes` and `namespaces`
because nothing changed there. At Google scale this turns 30-minute builds into 2-minute builds.

---

## Key Bazel concepts

### WORKSPACE
Marks the root of your project. Bazel looks for this file to find the project boundary.
In modern Bazel (7+) this file is intentionally empty — dependencies live in `MODULE.bazel`.

### MODULE.bazel
The modern dependency file. Declares what external tools your project needs.

```python
bazel_dep(name = "rules_python", version = "0.31.0")
```

This is like `package.json` in Node or `requirements.txt` in Python — but for build tools.

### BUILD
Every directory that contains source files needs a `BUILD` file.
It tells Bazel what to build and what each target depends on.

```python
py_library(
    name = "checks",
    srcs = ["nodes.py", "pods.py", "namespaces.py"],
)

py_binary(
    name = "checker",
    srcs = ["checker.py"],
    main = "checker.py",
    deps = [":checks"],
)
```

### py_library vs py_binary

| Rule | What it is | Can you run it? |
|---|---|---|
| `py_library` | A reusable module — imported by other targets | No |
| `py_binary` | A runnable program | Yes — `bazel run //:checker` |

### .bazelversion
Pins the exact Bazel version. If you use `bazelisk` (recommended),
it reads this file and downloads the right Bazel automatically.

```
7.1.0
```

---

## Project structure

```
k8s-bazel/
├── MODULE.bazel       ← declares rules_python + Python 3.11 toolchain
├── WORKSPACE          ← empty, marks project root
├── .bazelversion      ← pins Bazel to 7.1.0
├── BUILD              ← build rules: py_library + py_binary
├── checker.py         ← main entry point (imports nodes, pods, namespaces)
├── nodes.py           ← checks node health via kubectl get nodes
├── pods.py            ← checks pod health via kubectl get pods
└── namespaces.py      ← checks namespace health via kubectl get namespaces
```

---

## How the dependency graph works

```
BUILD declares:

py_library "checks"
    srcs = [nodes.py, pods.py, namespaces.py]

py_binary "checker"
    srcs = [checker.py]
    deps = [:checks]           ← checker can import nodes, pods, namespaces

When you run: bazel run //:checker

1. Bazel reads .bazelversion  → downloads Bazel 7.1.0 if needed
2. Bazel reads MODULE.bazel   → downloads rules_python + Python 3.11
3. Bazel reads BUILD          → builds "checks" library first
4. Bazel builds "checker"     → with "checks" available
5. Bazel runs checker.py      → which runs kubectl commands
```

---

## Adding a new health check

Three steps every time:

**Step 1** — create the file

```python
# events.py
import subprocess

def report():
    result = subprocess.run(
        ["kubectl", "get", "events", "-A", "--no-headers"],
        capture_output=True, text=True
    )
    lines = result.stdout.strip().splitlines()
    print(f"  OK   Events — {len(lines)} recent events")
```

**Step 2** — add it to `srcs` in BUILD

```python
py_library(
    name = "checks",
    srcs = [
        "nodes.py",
        "pods.py",
        "namespaces.py",
        "events.py",        # ← add here
    ],
)
```

**Step 3** — import and call it in `checker.py`

```python
import events              # ← add import

events.report()            # ← add call
```

That's it. Run `bazel run //:checker` and the new check appears.

---

## Prerequisites

| Tool | Install |
|---|---|
| bazelisk | `brew install bazelisk` (macOS) |
| kubectl | [kubernetes.io/docs/tasks/tools](https://kubernetes.io/docs/tasks/tools/) |
| minikube | [minikube.sigs.k8s.io](https://minikube.sigs.k8s.io/docs/start/) |

---

## Setup and run

```bash
# 1. Clone the repo
git clone https://github.com/<your-username>/k8s-bazel.git
cd k8s-bazel

# 2. Start minikube
minikube start

# 3. Run — Bazel downloads Python 3.11 automatically, no pip install needed
bazel run //:checker
```

---

## Why Bazel over just running `python checker.py`?

| | `python checker.py` | `bazel run //:checker` |
|---|---|---|
| Python version | Whatever's installed | Always 3.11, hermetic |
| Dependencies | Manual pip install | Declared in BUILD, automatic |
| Reproducibility | "works on my machine" | Same on every machine |
| Incremental builds | Rebuilds everything | Only rebuilds what changed |
| Scales to large projects | No | Yes |

For a single script, `python checker.py` is simpler. Bazel earns its place as your
project grows — more files, more teammates, more CI pipelines, more languages.

---

## Bazel vs other build tools

| Tool | Best for |
|---|---|
| **Bazel** | Large polyglot monorepos, reproducible builds at scale |
| **Make** | Small C/C++ projects on Linux |
| **CMake** | Cross-platform C/C++ libraries |
| **Gradle** | Java / Android |
| **Cargo** | Rust (built-in, no Bazel needed) |
| **npm / pip** | Single-language package management |

---

## License

MIT
