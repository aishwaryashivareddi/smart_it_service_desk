def log_event(message, level="INFO"):
    with open("data/logs.txt", "a") as f:
        f.write(f"[{level}] {message}\n")
        