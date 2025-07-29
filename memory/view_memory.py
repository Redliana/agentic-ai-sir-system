# memory/view_memory.py

from memory.json_memory import JSONMemory

def view_memory():
    mem = JSONMemory()
    data = mem.load()
    if not data:
        print("Memory is empty.")
        return

    print("🔍 Memory Contents:\n")
    for key, val in data.items():
        print(f"{key}:\n  {val}\n")

if __name__ == "__main__":
    view_memory()
