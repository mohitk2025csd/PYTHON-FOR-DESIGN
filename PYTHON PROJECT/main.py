
import json
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from datetime import datetime

# ---------------- CONFIGURATION ----------------

APP_BG = "#F3F5F9"
CARD_BG = "#FFFFFF"
PRIMARY = "#5B5FEF"
TEXT = "#20243A"
MUTED = "#737B91"
BORDER = "#E3E7F0"

DATA_FILE = Path(__file__).with_name("tasks.json")


# ---------------- APPLICATION ----------------

class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TaskFlow | To-Do Manager")
        self.root.geometry("850x650")
        self.root.minsize(680, 540)
        self.root.configure(bg=APP_BG)

        self.tasks = self.load_tasks()
        self.filter_value = tk.StringVar(value="All tasks")
        self.task_input = tk.StringVar()

        self.setup_styles()
        self.build_ui()
        self.refresh_tasks()

    # Load previously saved tasks
    def load_tasks(self):
        try:
            if DATA_FILE.exists():
                with DATA_FILE.open("r", encoding="utf-8") as file:
                    data = json.load(file)
                    if isinstance(data, list):
                        return [
                            item for item in data
                            if isinstance(item, dict)
                            and isinstance(item.get("title"), str)
                            and isinstance(item.get("completed"), bool)
                        ]
        except (OSError, json.JSONDecodeError):
            messagebox.showwarning(
                "Storage warning",
                "Saved tasks could not be read. "
                "A new task list will be started."
            )
        return []

    # Save tasks to a local JSON file
    def save_tasks(self):
        try:
            with DATA_FILE.open("w", encoding="utf-8") as file:
                json.dump(self.tasks, file, indent=4)
        except OSError as error:
            messagebox.showerror(
                "Save error",
                f"Could not save tasks:\n{error}"
            )

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "TCombobox",
            padding=7,
            fieldbackground=CARD_BG,
            background=CARD_BG,
            foreground=TEXT
        )

    def build_ui(self):
        # Main page
        page = tk.Frame(self.root, bg=APP_BG, padx=30, pady=24)
        page.pack(fill="both", expand=True)

        # Header
        header = tk.Frame(page, bg=APP_BG)
        header.pack(fill="x", pady=(0, 22))

        tk.Label(
            header,
            text="TASKFLOW",
            font=("Helvetica", 11, "bold"),
            fg=PRIMARY,
            bg=APP_BG
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Your day, organized.",
            font=("Helvetica", 25, "bold"),
            fg=TEXT,
            bg=APP_BG
        ).pack(anchor="w", pady=(5, 2))

        tk.Label(
            header,
            text="Plan less in your head. Get more done.",
            font=("Helvetica", 11),
            fg=MUTED,
            bg=APP_BG
        ).pack(anchor="w")

        # Statistics cards
        stats = tk.Frame(page, bg=APP_BG)
        stats.pack(fill="x", pady=(0, 20))

        self.total_label = self.make_stat_card(
            stats, "TOTAL TASKS", "0"
        )
        self.pending_label = self.make_stat_card(
            stats, "TO DO", "0"
        )
        self.completed_label = self.make_stat_card(
            stats, "COMPLETED", "0"
        )

        # Task entry card
        entry_card = tk.Frame(
            page, bg=CARD_BG, padx=18, pady=18,
            highlightbackground=BORDER, highlightthickness=1
        )
        entry_card.pack(fill="x", pady=(0, 18))

        tk.Label(
            entry_card,
            text="ADD A NEW TASK",
            font=("Helvetica", 10, "bold"),
            fg=TEXT,
            bg=CARD_BG
        ).pack(anchor="w", pady=(0, 10))

        entry_row = tk.Frame(entry_card, bg=CARD_BG)
        entry_row.pack(fill="x")

        self.entry = tk.Entry(
            entry_row,
            textvariable=self.task_input,
            font=("Helvetica", 12),
            bg="#F7F8FC",
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=PRIMARY
        )
        self.entry.pack(side="left", fill="x", expand=True, ipady=12)
        self.entry.bind("<Return>", lambda event: self.add_task())

        self.add_button = tk.Button(
            entry_row,
            text="+  Add Task",
            command=self.add_task,
            font=("Helvetica", 11, "bold"),
            bg=PRIMARY,
            fg="white",
            activebackground="#494DCE",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            padx=18,
            pady=10
        )
        self.add_button.pack(side="left", padx=(10, 0))

        # Task list card
        list_card = tk.Frame(
            page, bg=CARD_BG, padx=18, pady=16,
            highlightbackground=BORDER, highlightthickness=1
        )
        list_card.pack(fill="both", expand=True)

        toolbar = tk.Frame(list_card, bg=CARD_BG)
        toolbar.pack(fill="x", pady=(0, 12))

        tk.Label(
            toolbar,
            text="MY TASKS",
            font=("Helvetica", 11, "bold"),
            fg=TEXT,
            bg=CARD_BG
        ).pack(side="left")

        self.filter_box = ttk.Combobox(
            toolbar,
            textvariable=self.filter_value,
            values=["All tasks", "Pending", "Completed"],
            state="readonly",
            width=12
        )
        self.filter_box.pack(side="right")
        self.filter_box.bind(
            "<<ComboboxSelected>>",
            lambda event: self.refresh_tasks()
        )

        # Listbox and scrollbar
        list_frame = tk.Frame(list_card, bg=CARD_BG)
        list_frame.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        self.task_list = tk.Listbox(
            list_frame,
            font=("Helvetica", 12),
            bg="#FAFBFE",
            fg=TEXT,
            selectbackground="#E4E5FF",
            selectforeground=TEXT,
            activestyle="none",
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            selectmode="browse",
            yscrollcommand=scrollbar.set
        )
        self.task_list.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.task_list.yview)

        # Double-click toggles completion
        self.task_list.bind(
            "<Double-Button-1>",
            lambda event: self.toggle_task()
        )

        # Action buttons
        actions = tk.Frame(list_card, bg=CARD_BG)
        actions.pack(fill="x", pady=(14, 0))

        self.make_button(
            actions, "✓  Toggle Status",
            self.toggle_task, PRIMARY
        ).pack(side="left")

        self.make_button(
            actions, "Delete Selected",
            self.delete_task, "#D9485F"
        ).pack(side="left", padx=(8, 0))

        self.make_button(
            actions, "Clear Completed",
            self.clear_completed, "#E9ECF5", TEXT
        ).pack(side="right")

        tk.Label(
            page,
            text="TASKFLOW  •  Simple habits, better days",
            font=("Helvetica", 9),
            fg=MUTED,
            bg=APP_BG
        ).pack(pady=(14, 0))

        self.entry.focus_set()

    def make_stat_card(self, parent, title, value):
        card = tk.Frame(
            parent, bg=CARD_BG, padx=14, pady=12,
            highlightbackground=BORDER, highlightthickness=1
        )
        card.pack(side="left", fill="x", expand=True, padx=(0, 10))

        tk.Label(
            card, text=title,
            font=("Helvetica", 9, "bold"),
            fg=MUTED, bg=CARD_BG
        ).pack(anchor="w")

        number = tk.Label(
            card, text=value,
            font=("Helvetica", 23, "bold"),
            fg=TEXT, bg=CARD_BG
        )
        number.pack(anchor="w", pady=(4, 0))
        return number

    def make_button(self, parent, text, command, bg, fg="white"):
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=("Helvetica", 10, "bold"),
            bg=bg,
            fg=fg,
            activebackground=bg,
            activeforeground=fg,
            relief="flat",
            cursor="hand2",
            padx=12,
            pady=9
        )

    # Add a new task
    def add_task(self):
        title = self.task_input.get().strip()

        if not title:
            messagebox.showinfo(
                "Empty task", "Please enter a task first."
            )
            self.entry.focus_set()
            return

        self.tasks.append({
            "title": title,
            "completed": False,
            "created_at": datetime.now().isoformat(
                timespec="seconds"
            )
        })

        self.task_input.set("")
        self.save_tasks()
        self.filter_value.set("All tasks")
        self.refresh_tasks()
        self.entry.focus_set()

    # Return the actual task indexes shown by the current filter
    def visible_task_indexes(self):
        mode = self.filter_value.get()
        indexes = []

        for index, task in enumerate(self.tasks):
            if mode == "Pending" and task["completed"]:
                continue
            if mode == "Completed" and not task["completed"]:
                continue
            indexes.append(index)

        return indexes

    def refresh_tasks(self):
        self.task_list.delete(0, tk.END)

        indexes = self.visible_task_indexes()

        for index in indexes:
            task = self.tasks[index]

            if task["completed"]:
                line = f"  ✓   {task['title']}   — Completed"
            else:
                line = f"  ○   {task['title']}   — Pending"

            self.task_list.insert(tk.END, line)

            row = self.task_list.size() - 1
            if task["completed"]:
                self.task_list.itemconfig(
                    row, fg="#16845B", bg="#F0FAF5"
                )
            else:
                self.task_list.itemconfig(
                    row, fg=TEXT, bg="#FAFBFE"
                )

        total = len(self.tasks)
        completed = sum(
            1 for task in self.tasks if task["completed"]
        )
        pending = total - completed

        self.total_label.config(text=str(total))
        self.pending_label.config(text=str(pending))
        self.completed_label.config(text=str(completed))

    def selected_task_index(self):
        selection = self.task_list.curselection()

        if not selection:
            messagebox.showinfo(
                "Select a task",
                "Please select a task from the list first."
            )
            return None

        visible_indexes = self.visible_task_indexes()
        row = selection[0]

        if row >= len(visible_indexes):
            return None

        return visible_indexes[row]

    # Mark pending tasks completed, or reopen completed tasks
    def toggle_task(self):
        index = self.selected_task_index()

        if index is None:
            return

        self.tasks[index]["completed"] = (
            not self.tasks[index]["completed"]
        )
        self.save_tasks()
        self.refresh_tasks()

    def delete_task(self):
        index = self.selected_task_index()

        if index is None:
            return

        title = self.tasks[index]["title"]

        if messagebox.askyesno(
            "Delete task",
            f'Do you want to delete "{title}"?'
        ):
            del self.tasks[index]
            self.save_tasks()
            self.refresh_tasks()

    def clear_completed(self):
        count = sum(
            1 for task in self.tasks if task["completed"]
        )

        if count == 0:
            messagebox.showinfo(
                "Nothing to clear",
                "There are no completed tasks."
            )
            return

        if messagebox.askyesno(
            "Clear completed",
            f"Delete all {count} completed task(s)?"
        ):
            self.tasks = [
                task for task in self.tasks
                if not task["completed"]
            ]
            self.save_tasks()
            self.refresh_tasks()


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()
