"""
nodes.py — checks the health of Kubernetes nodes.
Imported by checker.py
"""
import subprocess


def get_nodes():
    """Run kubectl get nodes and return a list of node info dicts."""
    result = subprocess.run(
        ["kubectl", "get", "nodes",
         "--no-headers",
         "-o", "custom-columns=NAME:.metadata.name,STATUS:.status.conditions[-1].type,ROLE:.metadata.labels.kubernetes\\.io/role,AGE:.metadata.creationTimestamp"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        return None, result.stderr.strip()

    nodes = []
    for line in result.stdout.strip().splitlines():
        parts = line.split()
        if len(parts) >= 2:
            nodes.append({
                "name":   parts[0],
                "status": parts[1],  # Ready or NotReady
            })
    return nodes, None


def report():
    """Print a node health report."""
    nodes, err = get_nodes()

    if err:
        print(f"  FAIL Nodes — {err}")
        return

    if not nodes:
        print("  WARN Nodes — no nodes found")
        return

    for node in nodes:
        status = node["status"]
        icon   = "OK  " if status == "Ready" else "FAIL"
        print(f"  {icon} Node: {node['name']}  ({status})")