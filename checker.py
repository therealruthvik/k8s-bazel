"""
checker.py — main entry point.
Imports nodes and pods modules and runs all health checks.
"""
import subprocess

# Import our own modules — Bazel wires these up via deps in BUILD
import nodes
import pods
import namespaces


def check_cluster():
    """Check if the cluster is reachable at all."""
    result = subprocess.run(
        ["kubectl", "cluster-info", "--request-timeout=5s"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print("  OK   Cluster is reachable")
    else:
        print("  FAIL Cluster is NOT reachable — is minikube running?")
        print("       Run: minikube start")
        return False
    return True


def main():
    print()
    print("  ☸  Kubernetes Health Check")
    print("  " + "─" * 35)

    # Step 1: check cluster first — no point checking nodes/pods if unreachable
    reachable = check_cluster()
    if not reachable:
        return

    # Step 2: check nodes (imported from nodes.py)
    print()
    print("  Nodes:")
    nodes.report()

    # Step 3: check pods (imported from pods.py)
    print()
    print("  Pods:")
    pods.report()

    # Step 4: check namespaces (imported from namespaces.py)
    print()
    print("  Namespaces:")
    namespaces.report()
    
    
    print()


if __name__ == "__main__":
    main()