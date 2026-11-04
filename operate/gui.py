import os
import sys
import queue
import threading
import subprocess
from pathlib import Path
from tkinter import ttk, messagebox, scrolledtext, filedialog
import tkinter as tk

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"

API_KEYS = [
    ("OPENAI_API_KEY", "OpenAI API key"),
    ("GOOGLE_API_KEY", "Google (Gemini) API key"),
    ("ANTHROPIC_API_KEY", "Anthropic API key"),
    ("QWEN_API_KEY", "Qwen API key"),
    ("OLLAMA_API_KEY", "Ollama Cloud API key"),
]

ENV_FIELDS = [
    ("OLLAMA_HOST", "Ollama host (local or cloud)"),
    ("OLLAMA_CLOUD_MODEL", "Ollama Cloud model"),
]


def load_env_file():
    if not ENV_PATH.exists():
        return
    try:
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)
    except Exception:
        pass


def save_env_file(values):
    current = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            current[key.strip()] = value.strip().strip('"').strip("'")

    current.update({k: v for k, v in values.items() if v is not None})

    ordered_keys = [k for k, _ in API_KEYS] + [k for k, _ in ENV_FIELDS]
    lines = []
    for key in ordered_keys:
        if key in current and current[key] != "":
            lines.append(f"{key}={current[key]}")
    for key, value in current.items():
        if key not in ordered_keys and value != "":
            lines.append(f"{key}={value}")

    ENV_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    os.environ.update({k: v for k, v in values.items() if v not in (None, "")})


class OperateGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        load_env_file()

        self.title("Self-Operating Computer Control Panel")
        self.geometry("900x700")
        self.minsize(760, 600)

        self.process = None
        self.log_queue = queue.Queue()
        self._after_id = None

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=8, pady=8)

        self.api_tab = ttk.Frame(notebook)
        self.run_tab = ttk.Frame(notebook)
        notebook.add(self.api_tab, text="API и настройки")
        notebook.add(self.run_tab, text="Запуск и лог")

        self._build_api_tab()
        self._build_run_tab()
        self._poll_log_queue()

    def _build_api_tab(self):
        frame = ttk.Frame(self.api_tab)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        info = ttk.Label(
            frame,
            text="Ключи и параметры сохраняются в файл .env в папке проекта.",
        )
        info.pack(anchor="w", pady=(0, 10))

        grid = ttk.Frame(frame)
        grid.pack(fill="x")

        self.api_vars = {}
        row = 0
        for key, label in API_KEYS + ENV_FIELDS:
            ttk.Label(grid, text=label).grid(row=row, column=0, sticky="w", pady=4, padx=(0, 8))
            var = tk.StringVar(value=os.environ.get(key, ""))
            show = "*" if "KEY" in key else ""
            entry = ttk.Entry(grid, textvariable=var, width=70, show=show)
            entry.grid(row=row, column=1, sticky="ew", pady=4)
            self.api_vars[key] = var
            row += 1

        grid.columnconfigure(1, weight=1)

        buttons = ttk.Frame(frame)
        buttons.pack(fill="x", pady=12)
        ttk.Button(buttons, text="Сохранить", command=self.save_settings).pack(side="left")
        ttk.Button(buttons, text="Перезагрузить из .env", command=self.reload_settings).pack(side="left", padx=8)
        ttk.Button(buttons, text="Открыть папку проекта", command=self.open_project_folder).pack(side="left")

        note = ttk.Label(
            frame,
            text="Для Ollama Cloud достаточно OLLAMA_API_KEY. "
                 "OLLAMA_HOST обычно не меняйте, по умолчанию используется https://ollama.com.",
        )
        note.pack(anchor="w", pady=(10, 0))

    def _build_run_tab(self):
        frame = ttk.Frame(self.run_tab)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        model_row = ttk.Frame(frame)
        model_row.pack(fill="x", pady=(0, 8))
        ttk.Label(model_row, text="Модель:").pack(side="left")
        self.model_var = tk.StringVar(value="ollama-cloud")
        models = [
            "gpt-4-with-ocr",
            "gpt-4.1-with-ocr",
            "o1-with-ocr",
            "gpt-4-with-som",
            "gpt-4",
            "gemini-pro-vision",
            "claude-3",
            "qwen-vl",
            "llava",
            "ollama-cloud",
        ]
        combo = ttk.Combobox(model_row, textvariable=self.model_var, values=models, width=30)
        combo.pack(side="left", padx=8)
        ttk.Label(model_row, text="Можно вписать имя модели Ollama Cloud, например gemma4:31b").pack(side="left")

        objective_label = ttk.Label(frame, text="Задача для агента:")
        objective_label.pack(anchor="w")
        self.objective_text = scrolledtext.ScrolledText(frame, height=5, wrap="word")
        self.objective_text.pack(fill="x", pady=(0, 8))

        options_row = ttk.Frame(frame)
        options_row.pack(fill="x", pady=(0, 8))
        self.verbose_var = tk.BooleanVar(value=False)
        self.voice_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_row, text="Verbose (подробный лог)", variable=self.verbose_var).pack(side="left")
        ttk.Checkbutton(options_row, text="Voice mode (нужен whisper_mic)", variable=self.voice_var).pack(side="left", padx=12)

        buttons = ttk.Frame(frame)
        buttons.pack(fill="x", pady=(0, 8))
        ttk.Button(buttons, text="Открыть в новом терминале", command=self.run_new_terminal).pack(side="left")
        ttk.Button(buttons, text="Запустить здесь", command=self.run_embedded).pack(side="left", padx=8)
        ttk.Button(buttons, text="Остановить", command=self.stop_process).pack(side="left")
        ttk.Button(buttons, text="Очистить лог", command=self.clear_log).pack(side="right")

        self.log = scrolledtext.ScrolledText(frame, height=20, wrap="word", state="disabled")
        self.log.pack(fill="both", expand=True)

    def save_settings(self):
        values = {key: self.api_vars[key].get().strip() for key, _ in API_KEYS + ENV_FIELDS}
        save_env_file(values)
        messagebox.showinfo("Сохранено", "Настройки сохранены в .env.")

    def reload_settings(self):
        load_env_file()
        for key, _ in API_KEYS + ENV_FIELDS:
            self.api_vars[key].set(os.environ.get(key, ""))
        messagebox.showinfo("Обновлено", "Настройки перечитаны.")

    def open_project_folder(self):
        if os.name == "nt":
            os.startfile(str(PROJECT_ROOT))
        else:
            subprocess.Popen(["xdg-open", str(PROJECT_ROOT)])

    def _build_env(self):
        env = dict(os.environ)
        env["PYTHONPATH"] = str(PROJECT_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
        return env

    def _build_command(self):
        model = self.model_var.get().strip() or "ollama-cloud"
        prompt = self.objective_text.get("1.0", "end").strip()
        cmd = [sys.executable, "-m", "operate.main", "-m", model]
        if prompt:
            cmd += ["--prompt", prompt]
        if self.verbose_var.get():
            cmd.append("--verbose")
        if self.voice_var.get():
            cmd.append("--voice")
        return cmd

    def run_new_terminal(self):
        cmd = self._build_command()
        env = self._build_env()
        self._append_log("[Запуск в новом терминале]\n" + " ".join(cmd) + "\n")
        kwargs = {"cwd": str(PROJECT_ROOT), "env": env}
        if os.name == "nt":
            kwargs["creationflags"] = subprocess.CREATE_NEW_CONSOLE
            subprocess.Popen(cmd, **kwargs)
        else:
            terminal = None
            for candidate in ("gnome-terminal", "konsole", "xterm"):
                if subprocess.call(["which", candidate], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
                    terminal = candidate
                    break
            if terminal:
                subprocess.Popen([terminal, "--", *cmd], **kwargs)
            else:
                messagebox.showwarning("Терминал не найден", "Не найден эмулятор терминала. Запуск выполняется в фоне.")
                subprocess.Popen(cmd, **kwargs)

    def run_embedded(self):
        if self.process and self.process.poll() is None:
            messagebox.showwarning("Уже запущено", "Процесс operate уже выполняется. Сначала остановите его.")
            return

        prompt = self.objective_text.get("1.0", "end").strip()
        if not prompt:
            messagebox.showwarning(
                "Нужна задача",
                "Для встроенного запуска введите задачу в поле «Задача для агента».",
            )
            return

        self.save_settings()
        cmd = self._build_command()
        env = self._build_env()
        self._append_log("[Встроенный запуск]\n" + " ".join(cmd) + "\n\n")

        self.process = subprocess.Popen(
            cmd,
            cwd=str(PROJECT_ROOT),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        threading.Thread(target=self._stream_output, daemon=True).start()

    def _stream_output(self):
        if not self.process or not self.process.stdout:
            return
        for line in self.process.stdout:
            self.log_queue.put(line)
        return_code = self.process.wait()
        self.log_queue.put(f"\nПроцесс завершился с кодом {return_code}.\n")
        self.process = None

    def stop_process(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self._append_log("\n[Процесс остановлен пользователем]\n")

    def clear_log(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    def _append_log(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text)
        self.log.see("end")
        self.log.configure(state="disabled")

    def _poll_log_queue(self):
        try:
            while True:
                line = self.log_queue.get_nowait()
                self._append_log(line)
        except queue.Empty:
            pass
        self._after_id = self.after(100, self._poll_log_queue)

    def destroy(self):
        if self._after_id:
            self.after_cancel(self._after_id)
        if self.process and self.process.poll() is None:
            self.process.terminate()
        super().destroy()


def main_entry():
    app = OperateGUI()
    app.mainloop()


if __name__ == "__main__":
    main_entry()