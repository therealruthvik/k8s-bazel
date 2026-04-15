"""
pods.py — checks the health of Kubernetes pods.
Imported by checker.py
"""
import subprocess


def get_pods(namespace=None):
    """Run kubectl get pods and return a list of pod info dicts."""
    cmd = ["kubectl", "get", "pods", "--no-headers"]
    if namespace:
        cmd += ["-n", namespace]
    else:
        cmd += ["-A"]   # all namespaces

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        return None, result.stderr.strip()

    pods = []
    for line in result.stdout.strip().splitlines():
        parts = line.split()
        if not parts:
            continue
        # -A output: NAMESPACE  NAME  READY  STATUS  RESTARTS  AGE
        # -n output: NAME  READY  STATUS  RESTARTS  AGE
        if namespace:
            name, ready, status = parts[0], parts[1], parts[2]
            ns = namespace
        else:
            ns, name, ready, status = parts[0], parts[1], parts[2], parts[3]

        pods.append({
            "namespace": ns,
            "name":      name,
            "ready":     ready,
            "status":    status,
        })
    return pods, None


def report(namespace=None):
    """Print a pod health report."""
    pods, err = get_pods(namespace=namespace)

    if err:
        print(f"  FAIL Pods — {err}")
        return

    if not pods:
        print("  WARN Pods — no pods found")
        return

    # Count healthy vs unhealthy
    healthy   = [p for p in pods if p["status"] == "Running"]
    unhealthy = [p for p in pods if p["status"] != "Running"]

    print(f"  OK   Pods — {len(healthy)} running, {len(unhealthy)} not running")

    # Show details of unhealthy pods
    for pod in unhealthy:
        print(f"       WARN  {pod['namespace']}/{pod['name']}  status={pod['status']}")