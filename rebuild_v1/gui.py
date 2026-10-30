import threading
import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, List

from config import load_config, save_config


class AppGUI:
    def __init__(
        self,
        root: tk.Tk,
        run_callback: Callable[[List[str]], None],
        stop_callback: Callable[[], None],
        log_export: Callable[[Callable[[str], None]], None],
    ):
        self.root = root
        self.run_callback = run_callback
        self.stop_callback = stop_callback
        self.log_export = log_export
        self.config = load_config()
        self.tasks: List[str] = []

        root.title("Self-Operating Computer v1")
        root.geometry("760x520")

        notebook = ttk.Notebook(root)
        notebook.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(root, wrap="word", height=10, state=tk.DISABLED)

        self._build_tasks_tab(notebook)
        self._build_settings_tab(notebook)
        self._build_logs_tab(notebook)

        self.log_export(self.log)

    def _build_tasks_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Tasks")

        ttk.Label(frame, text="Objective").pack(anchor=tk.W, padx=8, pady=(8, 2))
        self.objective_input = tk.Text(frame, height=4)
        self.objective_input.pack(fill=tk.X, padx=8)

        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, padx=8, pady=6)

        ttk.Button(button_frame, text="Add Task", command=self.add_task).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(button_frame, text="Run", command=self.run_tasks).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(button_frame, text="Stop", command=self.stop_callback).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(button_frame, text="Clear", command=self.clear_tasks).pack(
            side=tk.LEFT, padx=4
        )

        self.dry_run_var = tk.BooleanVar(value=bool(self.config.get("dry_run", True)))
        dry_run_check = ttk.Checkbutton(
            frame,
            text="Dry Run (do not execute actions)",
            variable=self.dry_run_var,
            command=self._persist_dry_run,
        )
        dry_run_check.pack(anchor=tk.W, padx=8, pady=4)

        ttk.Label(frame, text="Task Queue").pack(anchor=tk.W, padx=8, pady=(10, 2))
        self.tasks_list = tk.Listbox(frame, height=8)
        self.tasks_list.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

    def _build_settings_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Settings")

        provider_frame = ttk.Frame(frame)
        provider_frame.pack(fill=tk.X, padx=8, pady=6)
        ttk.Label(provider_frame, text="Provider").pack(anchor=tk.W)
        self.provider_var = tk.StringVar(value=str(self.config.get("provider", "Ollama (Local)")))
        provider_menu = ttk.Combobox(
            provider_frame,
            textvariable=self.provider_var,
            values=["Ollama (Local)", "OpenRouter (API)"],
            state="readonly",
        )
        provider_menu.pack(fill=tk.X, pady=2)
        provider_menu.bind("<<ComboboxSelected>>", lambda _event: self._toggle_provider_fields())

        self.ollama_host_var = tk.StringVar(value=str(self.config.get("ollama_host")))
        self.ollama_model_var = tk.StringVar(value=str(self.config.get("ollama_model")))
        self.openrouter_key_var = tk.StringVar(value=str(self.config.get("openrouter_api_key")))
        self.openrouter_model_var = tk.StringVar(value=str(self.config.get("openrouter_model")))
        self.openrouter_base_var = tk.StringVar(value=str(self.config.get("openrouter_base_url")))

        self.provider_container = ttk.Frame(frame)
        self.provider_container.pack(fill=tk.X, padx=8, pady=4)
        self._build_provider_fields()

        extras = ttk.Frame(frame)
        extras.pack(fill=tk.X, padx=8, pady=6)

        ttk.Label(extras, text="Max steps").pack(anchor=tk.W)
        self.max_steps_var = tk.IntVar(value=int(self.config.get("max_steps", 10)))
        ttk.Entry(extras, textvariable=self.max_steps_var).pack(fill=tk.X, pady=2)

        ttk.Label(extras, text="Delay between actions (seconds)").pack(anchor=tk.W, pady=(8, 0))
        self.delay_var = tk.DoubleVar(value=float(self.config.get("delay_seconds", 0.6)))
        ttk.Entry(extras, textvariable=self.delay_var).pack(fill=tk.X, pady=2)

        ttk.Label(extras, text="Stop hotkey (e.g., ctrl+alt+s)").pack(anchor=tk.W, pady=(8, 0))
        self.stop_hotkey_var = tk.StringVar(value=str(self.config.get("stop_hotkey", "ctrl+alt+s")))
        ttk.Entry(extras, textvariable=self.stop_hotkey_var).pack(fill=tk.X, pady=2)

        ttk.Button(frame, text="Save Settings", command=self.save_settings).pack(
            padx=8, pady=10, anchor=tk.E
        )

    def _build_provider_fields(self) -> None:
        for child in list(self.provider_container.winfo_children()):
            child.destroy()

        provider = self.provider_var.get()
        if provider == "Ollama (Local)":
            ttk.Label(self.provider_container, text="Ollama Host").pack(anchor=tk.W)
            ttk.Entry(self.provider_container, textvariable=self.ollama_host_var).pack(
                fill=tk.X, pady=2
            )
            ttk.Label(self.provider_container, text="Ollama Model").pack(anchor=tk.W, pady=(6, 0))
            ttk.Entry(self.provider_container, textvariable=self.ollama_model_var).pack(
                fill=tk.X, pady=2
            )
        else:
            ttk.Label(self.provider_container, text="OpenRouter API Key").pack(anchor=tk.W)
            ttk.Entry(self.provider_container, textvariable=self.openrouter_key_var, show="*").pack(
                fill=tk.X, pady=2
            )
            ttk.Label(self.provider_container, text="OpenRouter Model").pack(anchor=tk.W, pady=(6, 0))
            ttk.Entry(self.provider_container, textvariable=self.openrouter_model_var).pack(
                fill=tk.X, pady=2
            )
            ttk.Label(self.provider_container, text="OpenRouter Base URL").pack(anchor=tk.W, pady=(6, 0))
            ttk.Entry(self.provider_container, textvariable=self.openrouter_base_var).pack(
                fill=tk.X, pady=2
            )

    def _build_logs_tab(self, notebook: ttk.Notebook) -> None:
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Logs")
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text = tk.Text(frame, wrap="word", state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)

    def add_task(self) -> None:
        text = self.objective_input.get("1.0", tk.END).strip()
        if text:
            self.tasks.append(text)
            self.tasks_list.insert(tk.END, text)
            self.objective_input.delete("1.0", tk.END)

    def clear_tasks(self) -> None:
        self.tasks.clear()
        self.tasks_list.delete(0, tk.END)

    def run_tasks(self) -> None:
        if not self.tasks:
            text = self.objective_input.get("1.0", tk.END).strip()
            if text:
                self.tasks.append(text)
                self.tasks_list.insert(tk.END, text)
        if not self.tasks:
            self.log("No tasks to run.")
            return
        threading.Thread(target=self.run_callback, args=(self.tasks.copy(),), daemon=True).start()

    def _persist_dry_run(self) -> None:
        self.config["dry_run"] = self.dry_run_var.get()
        save_config(self.config)

    def save_settings(self) -> None:
        self.config.update(
            {
                "provider": self.provider_var.get(),
                "ollama_host": self.ollama_host_var.get(),
                "ollama_model": self.ollama_model_var.get(),
                "openrouter_api_key": self.openrouter_key_var.get(),
                "openrouter_model": self.openrouter_model_var.get(),
                "openrouter_base_url": self.openrouter_base_var.get(),
                "max_steps": self.max_steps_var.get(),
                "delay_seconds": self.delay_var.get(),
                "stop_hotkey": self.stop_hotkey_var.get(),
                "dry_run": self.dry_run_var.get(),
            }
        )
        save_config(self.config)
        self.log("Settings saved.")
        self._build_provider_fields()

    def _toggle_provider_fields(self) -> None:
        self.save_settings()
        self._build_provider_fields()

    def log(self, message: str) -> None:
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)


