"""
namespaces.py — checks the health of Kubernetes namespaces.
Imported by checker.py
"""
import subprocess


def get_namespaces():
    """Run kubectl get namespaces and return a list of namespace info dicts."""
    result = subprocess.run(
        ["kubectl", "get", "namespaces", "--no-headers"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        return None, result.stderr.strip()

    namespaces = []
    for line in result.stdout.strip().splitlines():
        parts = line.split()
        if len(parts) >= 2:
            namespaces.append({
                "name":   parts[0],
                "status": parts[1],   # Active or Terminating
            })
    return namespaces, None


def report():
    """Print a namespace health report."""
    namespaces, err = get_namespaces()

    if err:
        print(f"  FAIL Namespaces — {err}")
        return

    if not namespaces:
        print("  WARN Namespaces — none found")
        return

    active      = [n for n in namespaces if n["status"] == "Active"]
    terminating = [n for n in namespaces if n["status"] == "Terminating"]

    print(f"  OK   Namespaces — {len(active)} active, {len(terminating)} terminating")

    # Warn about any stuck in Terminating
    for ns in terminating:
        print(f"       WARN  {ns['name']} is stuck Terminating")