import os
import tkinter as tk
from tkinter import filedialog, messagebox

from src.save_system.save_system import load_model
from src.pygame.Game import Game
from src.config_loader import build_from_yaml

SAVES_DIR = os.path.join(os.path.dirname(__file__), "saves")


def ensure_saves_dir() -> None:
    os.makedirs(SAVES_DIR, exist_ok=True)


def start_new(root) -> None:
    ensure_saves_dir()
    try:
        model = build_from_yaml()
    except Exception as exc:
        messagebox.showerror("Error", f"Failed to build model: {exc}")
        return
    root.destroy()
    Game(model).run()


def load_save(root) -> None:
    ensure_saves_dir()
    path = filedialog.askopenfilename(initialdir=SAVES_DIR, title="Select Save")
    if not path:
        return
    try:
        model = load_model(path)
    except Exception as exc:
        messagebox.showerror("Error", f"Failed to load save: {exc}")
        return
    root.destroy()
    Game(model).run()


def main() -> None:
    ensure_saves_dir()
    root = tk.Tk()
    root.title("Game Launcher")
    load_btn = tk.Button(root, text="Load Save", width=20, command=lambda: load_save(root))
    load_btn.pack(padx=20, pady=10)
    new_btn = tk.Button(root, text="New from YAML", width=20, command=lambda: start_new(root))
    new_btn.pack(padx=20, pady=10)
    root.mainloop()


if __name__ == "__main__":
    main()
