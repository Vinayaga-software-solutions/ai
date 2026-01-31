#!/usr/bin/env python3
import os
import sys
import time
import socket
import requests

SMOKE_TIMEOUT = int(os.getenv("SMOKE_TIMEOUT", "120"))
INTERVAL = float(os.getenv("SMOKE_INTERVAL", "2"))

services = [
    {"name": "orchestrator", "type": "http", "url": "http://orchestrator:8000/health"},
    {"name": "ingestion", "type": "http", "url": "http://ingestion:80/health"},
    {"name": "chunking", "type": "http", "url": "http://chunking:80/health"},
    {"name": "retrieval", "type": "http", "url": "http://retrieval:80/health"},
    {"name": "auth", "type": "http", "url": "http://auth:80/health"},
    {"name": "gateway", "type": "http", "url": "http://gateway:80/health"},
    {"name": "embedding-service", "type": "http", "url": "http://embedding-service:80/"},
    {"name": "llm-service", "type": "http", "url": "http://llm-service:11434/"},
    {"name": "qdrant", "type": "tcp", "host": "qdrant", "port": 6333},
    {"name": "seeder", "type": "file", "path": "/state/seeder_done"},
]


def check_http(url):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code >= 200 and r.status_code < 500:
            return True, r.status_code
        return False, r.status_code
    except Exception as e:
        return False, str(e)


def check_tcp(host, port):
    try:
        with socket.create_connection((host, port), timeout=5):
            return True, None
    except Exception as e:
        return False, str(e)


def check_file(path):
    return os.path.exists(path), None


if __name__ == "__main__":
    print("Smoke test starting: will wait up to {}s for services to become ready.".format(SMOKE_TIMEOUT))
    start = time.time()
    results = {}

    for svc in services:
        name = svc["name"]
        ok = False
        last_err = None
        while time.time() - start < SMOKE_TIMEOUT:
            if svc["type"] == "http":
                ok, detail = check_http(svc["url"])
                last_err = detail
            elif svc["type"] == "tcp":
                ok, detail = check_tcp(svc["host"], svc["port"])
                last_err = detail
            elif svc["type"] == "file":
                ok, detail = check_file(svc["path"])
                last_err = detail
            if ok:
                print(f"[OK] {name}")
                break
            else:
                print(f"[WAIT] {name} not ready yet: {last_err}")
            time.sleep(INTERVAL)
        results[name] = ok
        if not ok:
            print(f"[ERROR] {name} did not become ready within {SMOKE_TIMEOUT}s")

    failing = [n for n, ok in results.items() if not ok]
    if failing:
        print("Smoke test failed for services:", failing)
        sys.exit(1)
    else:
        print("All services are healthy. Smoke test passed.")
        sys.exit(0)
