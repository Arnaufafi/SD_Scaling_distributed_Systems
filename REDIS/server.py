import subprocess

server_scripts = [
    "REDIS/insult_filter.py"
]

processes = []

print("[server] Starting server tasks...")

for script in server_scripts:
    print(f"[server] Running {script}...")
    p = subprocess.Popen(["python3", script])
    processes.append(p)

# Wait for all server scripts to finish
for p in processes:
    p.wait()

print("[server] All server tasks completed.")
