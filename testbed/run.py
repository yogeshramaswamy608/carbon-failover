"""Test bed of preregistration section 9: three kind clusters, an Envoy proxy, netem delays.

Usage: python testbed/run.py REPEATS OUT_JSON

Cells: destination near (10 ms added round trip) or far (40 ms), headroom full or half (half starts
the destination at 2 of 4 replicas and scales it to 4 once steering is done). Each repeat starts from
the same state: a fresh home cluster, the destination at its starting replica count, Envoy restarted.
"""
from __future__ import annotations

import json
import os
import statistics
import subprocess
import sys
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ECHO = "hashicorp/http-echo:1.0"
NETSHOOT = "nicolaka/netshoot:v0.13"
ENVOY = "envoyproxy/envoy:v1.31.2"
RPS, STEADY_S, AFTER_S = 100, 60, 150
DELAY = {"near": 5, "far": 20}  # ms each way: 10 and 40 ms added round trip
HERE = os.path.dirname(os.path.abspath(__file__))


def sh(cmd: str, check: bool = True) -> str:
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and r.returncode:
        raise RuntimeError(f"{cmd}\n{r.stdout}\n{r.stderr}")
    return r.stdout.strip()


def ip(node: str) -> str:
    return sh(f"docker inspect -f '{{{{.NetworkSettings.Networks.kind.IPAddress}}}}' {node}")


def deploy(cluster: str, replicas: int) -> None:
    manifest = f"""
apiVersion: apps/v1
kind: Deployment
metadata: {{name: echo}}
spec:
  replicas: {replicas}
  selector: {{matchLabels: {{app: echo}}}}
  template:
    metadata: {{labels: {{app: echo}}}}
    spec:
      containers:
      - name: echo
        image: {ECHO}
        args: ["-text={cluster}", "-listen=:5678"]
        readinessProbe: {{httpGet: {{path: /, port: 5678}}, periodSeconds: 1}}
---
apiVersion: v1
kind: Service
metadata: {{name: echo}}
spec:
  type: NodePort
  selector: {{app: echo}}
  ports: [{{port: 5678, targetPort: 5678, nodePort: 30080}}]
"""
    p = subprocess.run(f"kubectl --context kind-{cluster} apply -f -", shell=True, input=manifest,
                       capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(p.stderr)
    sh(f"kubectl --context kind-{cluster} rollout status deploy/echo --timeout=180s")


def cluster(name: str) -> None:
    sh(f"kind delete cluster --name {name}", check=False)
    sh(f"kind create cluster --name {name} --wait 120s")
    sh(f"kind load docker-image {ECHO} --name {name}")


def netem(node: str, envoy_ip_peer: str, ms: int) -> None:
    """Half the added round trip on the node's egress, half on Envoy's egress toward the node."""
    sh(f"docker run --rm --net container:{node} --cap-add NET_ADMIN {NETSHOOT} tc qdisc replace dev eth0 root netem delay {ms}ms")
    sh(f"docker run --rm --net container:envoy --cap-add NET_ADMIN {NETSHOOT} sh -c '"
       f"tc qdisc add dev eth0 root handle 1: prio bands 4 2>/dev/null; "
       f"tc qdisc replace dev eth0 parent 1:4 handle 40: netem delay {ms}ms; "
       f"tc filter add dev eth0 parent 1: protocol ip prio 1 u32 match ip dst {envoy_ip_peer}/32 flowid 1:4'")


def envoy(home_ip: str, dest_ip: str) -> None:
    sh("docker rm -f envoy", check=False)
    cfg = open(os.path.join(HERE, "envoy.yaml.tmpl")).read().replace("HOME_IP", home_ip).replace("DEST_IP", dest_ip)
    open("/tmp/envoy.yaml", "w").write(cfg)
    sh(f"docker run -d --name envoy --network kind -p 10000:10000 -p 9901:9901 -v /tmp/envoy.yaml:/etc/envoy/envoy.yaml {ENVOY}")
    for _ in range(60):
        try:
            if urllib.request.urlopen("http://127.0.0.1:10000/", timeout=1).status == 200:
                return
        except Exception:
            time.sleep(1)
    raise RuntimeError("envoy did not serve")


def one(dest: str, headroom: str, rep: int) -> dict:
    cluster("home")
    deploy("home", 4)
    deploy(dest, 2 if headroom == "half" else 4)
    sh(f"kubectl --context kind-{dest} scale deploy/echo --replicas={2 if headroom == 'half' else 4}")
    sh(f"kubectl --context kind-{dest} rollout status deploy/echo --timeout=120s")
    home_ip, dest_ip = ip("home-control-plane"), ip(f"{dest}-control-plane")
    envoy(home_ip, dest_ip)
    netem(f"{dest}-control-plane", dest_ip, DELAY[dest])
    log, health, stop = [], [], threading.Event()

    def req() -> None:
        t0 = time.time()
        try:
            with urllib.request.urlopen("http://127.0.0.1:10000/", timeout=2) as r:
                body, code = r.read().decode().strip(), r.status
        except Exception as e:
            body, code = "", getattr(e, "code", 0) or 0
        log.append((t0, (time.time() - t0) * 1000, code, body))

    def load() -> None:
        with ThreadPoolExecutor(max_workers=64) as ex:
            nxt = time.time()
            while not stop.is_set():
                ex.submit(req)
                nxt += 1 / RPS
                time.sleep(max(0, nxt - time.time()))

    def poll() -> None:
        while not stop.is_set():
            try:
                txt = urllib.request.urlopen("http://127.0.0.1:9901/clusters", timeout=1).read().decode()
                bad = any(l.startswith(f"svc::{home_ip}:30080::health_flags::") and "failed_active_hc" in l
                          for l in txt.splitlines())
                health.append((time.time(), bad))
            except Exception:
                pass
            time.sleep(0.1)

    th = [threading.Thread(target=load), threading.Thread(target=poll)]
    [x.start() for x in th]
    time.sleep(STEADY_S)
    t_fail = time.time()
    sh("docker stop -t 0 home-control-plane")
    scale_ready = None
    t_eject = t_steer = None
    deadline = t_fail + AFTER_S
    while time.time() < deadline:
        time.sleep(0.2)
        if t_eject is None:
            t_eject = next((t for t, b in health if t > t_fail and b), None)
        if t_eject and t_steer is None:
            t_steer = steered(log, t_eject, dest)
            if t_steer and headroom == "half":
                sh(f"kubectl --context kind-{dest} scale deploy/echo --replicas=4")
                sh(f"kubectl --context kind-{dest} rollout status deploy/echo --timeout=120s")
                scale_ready = time.time()
        if t_steer and (headroom == "full" or scale_ready) and time.time() > (scale_ready or t_steer) + 15:
            break
    stop.set()
    [x.join() for x in th]
    base = [l for t0, l, c, b in log if t0 < t_fail and c == 200]
    base_p50 = statistics.median(base) if base else None
    t_rec = recovered(log, t_fail, base_p50, scale_ready or t_steer)
    sh("docker rm -f envoy", check=False)
    out = {"dest": dest, "headroom": headroom, "repeat": rep, "requests": len(log),
           "baseline_p50_ms": base_p50,
           "detection_s": (t_eject - t_fail) if t_eject else None,
           "steering_s": (t_steer - t_eject) if (t_steer and t_eject) else None,
           "scaleup_s": (scale_ready - t_steer) if scale_ready and t_steer else (0.0 if headroom == "full" and t_steer else None),
           "recovery_s": (t_rec - t_fail) if t_rec else None}
    print(json.dumps(out), flush=True)
    return out


def steered(log, t_from: float, dest: str) -> float | None:
    """The end of the first 1-second window after ejection with 99 percent of requests served by dest."""
    xs = sorted((t, b) for t, l, c, b in list(log) if t >= t_from)
    t = t_from
    while xs and t + 1 <= xs[-1][0]:
        w = [b for s, b in xs if t <= s < t + 1]
        if len(w) >= RPS * 0.5 and sum(b == dest for b in w) / len(w) >= 0.99:
            return t + 1
        t += 0.1
    return None


def recovered(log, t_fail: float, base_p50, not_before) -> float | None:
    """Start of the first 10-second window after the failure with 99.9 percent success and the
    median latency within the 50 ms bound over the steady median."""
    if base_p50 is None or not_before is None:
        return None
    xs = sorted((t, l, c) for t, l, c, b in list(log) if t >= t_fail)
    t = t_fail
    while xs and t + 10 <= xs[-1][0]:
        w = [(l, c) for s, l, c in xs if t <= s < t + 10]
        if len(w) >= RPS * 5:
            ok = sum(c == 200 for _, c in w) / len(w) >= 0.999
            lat = statistics.median(l for l, c in w if c == 200) <= base_p50 + 50 if ok else False
            if ok and lat:
                return t
        t += 0.1
    return None


def main() -> int:
    reps, out = int(sys.argv[1]), sys.argv[2]
    sh(f"docker pull -q {ECHO} && docker pull -q {NETSHOOT} && docker pull -q {ENVOY}")
    cluster("near")
    cluster("far")
    res = []
    for rep in range(reps):
        for dest in ("near", "far"):
            for headroom in ("full", "half"):
                try:
                    res.append(one(dest, headroom, rep))
                except Exception as e:
                    res.append({"dest": dest, "headroom": headroom, "repeat": rep, "error": str(e)[-500:]})
                    print(json.dumps(res[-1]), flush=True)
    json.dump(res, open(out, "w"), indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
