def unsafe_file_reader(filename: str):
    # Path Traversal & Unsafe File Access
    with open(f"/var/data/logs/{filename}", "r") as f:
        return f.read()