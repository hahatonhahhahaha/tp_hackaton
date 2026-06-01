import json
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk


BG = "#f4f6fb"
SURFACE = "#ffffff"
BORDER = "#d9e2ec"
TEXT = "#1f2937"
MUTED = "#6b7280"
ACCENT = "#2563eb"
ACCENT_SOFT = "#e8f1ff"

CATEGORY_ORDER = [
    "incidents",
    "service_requests",
    "spam",
    "hardware_faults",
    "прочее",
]
CATEGORY_NAMES = {
    "incidents": "Инциденты",
    "service_requests": "Запросы",
    "spam": "Спам",
    "hardware_faults": "Оборудование",
    "прочее": "Прочее",
}
CATEGORY_COLORS = {
    "incidents": "#dc3545",
    "service_requests": "#2563eb",
    "spam": "#f59e0b",
    "hardware_faults": "#16a34a",
    "прочее": "#6b7280",
}


def load_results(json_path: str | Path) -> list[dict]:
    json_path = Path(json_path)

    with json_path.open("r", encoding="utf-8-sig") as json_file:
        data = json.load(json_file)

    if not isinstance(data, list):
        raise ValueError("JSON должен быть списком")

    return data


def count_categories(results: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}

    for result in results:
        category = str(result.get("category") or "прочее")
        counts[category] = counts.get(category, 0) + 1

    return counts


def category_title(category: str) -> str:
    return CATEGORY_NAMES.get(category, category)


def sorted_categories(categories) -> list[str]:
    known = [category for category in CATEGORY_ORDER if category in categories]
    other = sorted(category for category in categories if category not in CATEGORY_ORDER)
    return known + other


class ResultViewer:
    def __init__(self, root: tk.Tk, json_path: Path) -> None:
        self.root = root
        self.json_path = json_path
        self.results: list[dict] = []
        self.filtered: list[dict] = []

        self.root.title("Панель классификации писем")
        self.root.geometry("1180x760")
        self.root.minsize(980, 640)
        self.root.configure(bg=BG)

        self.path_var = tk.StringVar(value=str(json_path))
        self.status_var = tk.StringVar(value="")
        self.filter_var = tk.StringVar(value="Все")
        self.detail_title_var = tk.StringVar(value="Выберите письмо")
        self.detail_meta_var = tk.StringVar(value="")

        self._configure_style()
        self._build_interface()
        self.load_file(json_path)

    def _configure_style(self) -> None:
        self.style = ttk.Style()

        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        self.style.configure("TFrame", background=BG)
        self.style.configure("Surface.TFrame", background=SURFACE)
        self.style.configure(
            "Title.TLabel",
            background=BG,
            foreground=TEXT,
            font=("Helvetica", 24, "bold"),
        )
        self.style.configure(
            "Subtitle.TLabel",
            background=BG,
            foreground=MUTED,
            font=("Helvetica", 12),
        )
        self.style.configure(
            "PanelTitle.TLabel",
            background=SURFACE,
            foreground=TEXT,
            font=("Helvetica", 14, "bold"),
        )
        self.style.configure(
            "PanelMuted.TLabel",
            background=SURFACE,
            foreground=MUTED,
            font=("Helvetica", 11),
        )
        self.style.configure(
            "TButton",
            font=("Helvetica", 11),
            padding=(12, 7),
        )
        self.style.configure(
            "TCombobox",
            padding=(6, 5),
            fieldbackground=SURFACE,
            background=SURFACE,
        )
        self.style.configure(
            "Treeview",
            background=SURFACE,
            fieldbackground=SURFACE,
            foreground=TEXT,
            rowheight=34,
            borderwidth=0,
            font=("Helvetica", 11),
        )
        self.style.configure(
            "Treeview.Heading",
            background="#edf2f7",
            foreground=TEXT,
            relief="flat",
            font=("Helvetica", 11, "bold"),
            padding=(6, 8),
        )
        self.style.map(
            "Treeview",
            background=[("selected", ACCENT)],
            foreground=[("selected", "#ffffff")],
        )

    def _build_interface(self) -> None:
        header = ttk.Frame(self.root, padding=(18, 16, 18, 8))
        header.pack(fill="x")

        title_box = ttk.Frame(header)
        title_box.pack(side="left", fill="x", expand=True)

        ttk.Label(
            title_box,
            text="Панель классификации писем",
            style="Title.TLabel",
        ).pack(anchor="w")
        ttk.Label(
            title_box,
            text="Сводка по результатам обработки, фильтрация и детали обращений.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        button_box = ttk.Frame(header)
        button_box.pack(side="right")
        ttk.Button(button_box, text="Открыть JSON", command=self.open_file).pack(
            side="left",
            padx=(0, 8),
        )
        ttk.Button(button_box, text="Обновить", command=self.reload_file).pack(
            side="left",
        )

        path_box = ttk.Frame(self.root, padding=(18, 0, 18, 12))
        path_box.pack(fill="x")
        ttk.Entry(path_box, textvariable=self.path_var).pack(fill="x")

        self.stats_frame = tk.Frame(self.root, bg=BG)
        self.stats_frame.pack(fill="x", padx=18, pady=(0, 12))

        chart_panel = self.make_panel(self.root)
        chart_panel.pack(fill="x", padx=18, pady=(0, 14))

        chart_header = tk.Frame(chart_panel, bg=SURFACE)
        chart_header.pack(fill="x", padx=16, pady=(14, 6))
        tk.Label(
            chart_header,
            text="Распределение по категориям",
            bg=SURFACE,
            fg=TEXT,
            font=("Helvetica", 14, "bold"),
        ).pack(side="left")
        self.summary_label = tk.Label(
            chart_header,
            text="",
            bg=SURFACE,
            fg=MUTED,
            font=("Helvetica", 11),
        )
        self.summary_label.pack(side="right")

        self.canvas = tk.Canvas(
            chart_panel,
            height=132,
            bg=SURFACE,
            highlightthickness=0,
        )
        self.canvas.pack(fill="x", padx=16, pady=(0, 14))
        self.canvas.bind("<Configure>", self.redraw_chart)

        workspace = tk.PanedWindow(
            self.root,
            orient="horizontal",
            sashwidth=8,
            bg=BG,
            bd=0,
            showhandle=False,
        )
        workspace.pack(fill="both", expand=True, padx=18, pady=(0, 16))

        left_panel = self.make_panel(workspace)
        right_panel = self.make_panel(workspace)
        workspace.add(left_panel, minsize=560)
        workspace.add(right_panel, minsize=340)

        table_header = tk.Frame(left_panel, bg=SURFACE)
        table_header.pack(fill="x", padx=16, pady=(14, 10))

        tk.Label(
            table_header,
            text="Список писем",
            bg=SURFACE,
            fg=TEXT,
            font=("Helvetica", 14, "bold"),
        ).pack(side="left")

        filter_box = tk.Frame(table_header, bg=SURFACE)
        filter_box.pack(side="right")
        tk.Label(
            filter_box,
            text="Категория",
            bg=SURFACE,
            fg=MUTED,
            font=("Helvetica", 11),
        ).pack(side="left", padx=(0, 8))
        self.filter_box = ttk.Combobox(
            filter_box,
            textvariable=self.filter_var,
            state="readonly",
            width=20,
        )
        self.filter_box.pack(side="left")
        self.filter_box.bind("<<ComboboxSelected>>", self.update_table)

        table_body = tk.Frame(left_panel, bg=SURFACE)
        table_body.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        columns = ("file_name", "category", "subject", "sender", "move_status")
        self.table = ttk.Treeview(
            table_body,
            columns=columns,
            show="headings",
            height=16,
        )
        self.table.tag_configure("odd", background="#f8fafc")
        self.table.tag_configure("even", background=SURFACE)

        headings = {
            "file_name": "Файл",
            "category": "Категория",
            "subject": "Тема",
            "sender": "От кого",
            "move_status": "Статус",
        }
        widths = {
            "file_name": 125,
            "category": 130,
            "subject": 260,
            "sender": 180,
            "move_status": 120,
        }

        for column in columns:
            self.table.heading(column, text=headings[column])
            self.table.column(column, width=widths[column], anchor="w")

        table_scroll = ttk.Scrollbar(
            table_body,
            orient="vertical",
            command=self.table.yview,
        )
        self.table.configure(yscrollcommand=table_scroll.set)
        self.table.pack(side="left", fill="both", expand=True)
        table_scroll.pack(side="right", fill="y")
        self.table.bind("<<TreeviewSelect>>", self.show_selected)

        detail_header = tk.Frame(right_panel, bg=SURFACE)
        detail_header.pack(fill="x", padx=16, pady=(14, 8))

        tk.Label(
            detail_header,
            textvariable=self.detail_title_var,
            bg=SURFACE,
            fg=TEXT,
            font=("Helvetica", 15, "bold"),
            wraplength=360,
            justify="left",
        ).pack(anchor="w")
        tk.Label(
            detail_header,
            textvariable=self.detail_meta_var,
            bg=SURFACE,
            fg=MUTED,
            font=("Helvetica", 11),
            wraplength=360,
            justify="left",
        ).pack(anchor="w", pady=(5, 0))

        self.score_canvas = tk.Canvas(
            right_panel,
            height=126,
            bg=SURFACE,
            highlightthickness=0,
        )
        self.score_canvas.pack(fill="x", padx=16, pady=(0, 8))

        self.detail_text = tk.Text(
            right_panel,
            wrap="word",
            bg="#fbfdff",
            fg=TEXT,
            relief="flat",
            padx=12,
            pady=12,
            font=("Helvetica", 11),
            height=14,
        )
        detail_scroll = ttk.Scrollbar(
            right_panel,
            orient="vertical",
            command=self.detail_text.yview,
        )
        self.detail_text.configure(yscrollcommand=detail_scroll.set)
        self.detail_text.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(16, 0),
            pady=(0, 16),
        )
        detail_scroll.pack(side="right", fill="y", padx=(0, 16), pady=(0, 16))

        bottom = ttk.Frame(self.root, padding=(18, 0, 18, 14))
        bottom.pack(fill="x")
        ttk.Label(bottom, textvariable=self.status_var, style="Subtitle.TLabel").pack(
            anchor="w"
        )

    def make_panel(self, parent) -> tk.Frame:
        return tk.Frame(
            parent,
            bg=SURFACE,
            highlightbackground=BORDER,
            highlightcolor=BORDER,
            highlightthickness=1,
            bd=0,
        )

    def make_stat_card(
        self,
        parent: tk.Frame,
        title: str,
        value: int,
        color: str,
        column: int,
    ) -> None:
        card = tk.Frame(
            parent,
            bg=SURFACE,
            highlightbackground=BORDER,
            highlightthickness=1,
            bd=0,
        )
        card.grid(row=0, column=column, sticky="ew", padx=(0, 10))
        parent.grid_columnconfigure(column, weight=1)

        tk.Frame(card, bg=color, width=4).pack(side="left", fill="y")

        content = tk.Frame(card, bg=SURFACE)
        content.pack(side="left", fill="both", expand=True, padx=12, pady=10)

        tk.Label(
            content,
            text=title,
            bg=SURFACE,
            fg=MUTED,
            font=("Helvetica", 10),
        ).pack(anchor="w")
        tk.Label(
            content,
            text=str(value),
            bg=SURFACE,
            fg=TEXT,
            font=("Helvetica", 22, "bold"),
        ).pack(anchor="w", pady=(3, 0))

    def open_file(self) -> None:
        file_name = filedialog.askopenfilename(
            title="Выберите result.json",
            filetypes=(("JSON", "*.json"), ("Все файлы", "*.*")),
        )

        if file_name:
            self.load_file(Path(file_name))

    def reload_file(self) -> None:
        self.load_file(Path(self.path_var.get()))

    def load_file(self, json_path: Path) -> None:
        try:
            self.results = load_results(json_path)
        except (OSError, json.JSONDecodeError, ValueError) as error:
            messagebox.showerror("Ошибка", str(error))
            return

        self.json_path = json_path
        self.path_var.set(str(json_path))
        self.update_summary()
        self.update_filter()
        self.update_table()

    def update_summary(self) -> None:
        counts = count_categories(self.results)
        total = len(self.results)

        for child in self.stats_frame.winfo_children():
            child.destroy()

        self.make_stat_card(self.stats_frame, "Всего", total, ACCENT, 0)

        column = 1
        for category in sorted_categories(counts):
            self.make_stat_card(
                self.stats_frame,
                category_title(category),
                counts[category],
                CATEGORY_COLORS.get(category, MUTED),
                column,
            )
            column += 1

        moved_count = sum(
            1 for result in self.results if result.get("move_status") == "перемещено"
        )
        self.summary_label.configure(
            text=f"Перемещено: {moved_count} из {total}"
        )
        self.draw_chart(counts)

    def redraw_chart(self, event=None) -> None:
        self.draw_chart(count_categories(self.results))

    def draw_chart(self, counts: dict[str, int]) -> None:
        self.canvas.delete("all")

        if not counts:
            self.canvas.create_text(
                20,
                60,
                anchor="w",
                fill=MUTED,
                text="Нет данных для отображения",
                font=("Helvetica", 12),
            )
            return

        width = self.canvas.winfo_width()
        if width < 100:
            width = 1000

        max_count = max(counts.values())
        left = 150
        right = width - 54
        top = 14
        bar_height = 16
        gap = 9
        max_bar_width = max(100, right - left)

        for index, category in enumerate(sorted_categories(counts)):
            count = counts[category]
            y = top + index * (bar_height + gap)
            color = CATEGORY_COLORS.get(category, MUTED)
            bar_width = int(max_bar_width * count / max_count)

            self.canvas.create_text(
                8,
                y + 8,
                anchor="w",
                text=category_title(category),
                fill=TEXT,
                font=("Helvetica", 11),
            )
            self.canvas.create_rectangle(
                left,
                y,
                left + max_bar_width,
                y + bar_height,
                fill="#edf2f7",
                outline="#edf2f7",
            )
            self.canvas.create_rectangle(
                left,
                y,
                left + bar_width,
                y + bar_height,
                fill=color,
                outline=color,
            )
            self.canvas.create_text(
                left + bar_width + 8,
                y + 8,
                anchor="w",
                text=str(count),
                fill=MUTED,
                font=("Helvetica", 10, "bold"),
            )

    def update_filter(self) -> None:
        counts = count_categories(self.results)
        values = ["Все"] + [category_title(category) for category in sorted_categories(counts)]
        self.filter_box["values"] = values

        if self.filter_var.get() not in values:
            self.filter_var.set("Все")

    def category_from_filter(self) -> str:
        current = self.filter_var.get()

        for category, title in CATEGORY_NAMES.items():
            if current == title:
                return category

        return current

    def filtered_results(self) -> list[dict]:
        current = self.filter_var.get()

        if current == "Все":
            return self.results

        category = self.category_from_filter()
        return [
            result
            for result in self.results
            if str(result.get("category") or "") == category
        ]

    def update_table(self, event=None) -> None:
        self.filtered = self.filtered_results()

        for item in self.table.get_children():
            self.table.delete(item)

        for index, result in enumerate(self.filtered):
            category = str(result.get("category") or "")
            tag = "even" if index % 2 == 0 else "odd"
            self.table.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    result.get("file_name", ""),
                    category_title(category),
                    result.get("subject", ""),
                    result.get("sender", ""),
                    result.get("move_status", ""),
                ),
                tags=(tag,),
            )

        self.status_var.set(f"Показано писем: {len(self.filtered)}")
        self.detail_title_var.set("Выберите письмо")
        self.detail_meta_var.set("")
        self.detail_text.delete("1.0", "end")
        self.score_canvas.delete("all")

        if self.filtered:
            first = self.table.get_children()[0]
            self.table.selection_set(first)
            self.table.focus(first)
            self.show_selected()

    def show_selected(self, event=None) -> None:
        selected = self.table.selection()

        if not selected:
            return

        index = int(selected[0])
        result = self.filtered[index]
        category = str(result.get("category") or "")
        file_name = result.get("file_name", "")
        sender = result.get("sender", "")

        self.detail_title_var.set(str(result.get("subject") or "Без темы"))
        self.detail_meta_var.set(
            f"{file_name} · {category_title(category)} · {sender}"
        )
        self.draw_scores(result.get("scores") or {})
        self.detail_text.delete("1.0", "end")
        self.detail_text.insert("end", self.format_result(result))

    def draw_scores(self, scores: dict) -> None:
        self.score_canvas.delete("all")

        if not scores:
            self.score_canvas.create_text(
                0,
                40,
                anchor="w",
                text="Баллы не рассчитаны",
                fill=MUTED,
                font=("Helvetica", 11),
            )
            return

        max_score = max(abs(float(score)) for score in scores.values()) or 1
        width = self.score_canvas.winfo_width()
        if width < 100:
            width = 360

        left = 120
        max_bar_width = width - left - 20

        self.score_canvas.create_text(
            0,
            10,
            anchor="w",
            text="Баллы по категориям",
            fill=TEXT,
            font=("Helvetica", 11, "bold"),
        )

        for index, category in enumerate(sorted_categories(scores)):
            score = float(scores[category])
            y = 32 + index * 18
            color = CATEGORY_COLORS.get(category, MUTED)
            bar_width = int(max_bar_width * abs(score) / max_score)

            self.score_canvas.create_text(
                0,
                y + 7,
                anchor="w",
                text=category_title(category),
                fill=MUTED,
                font=("Helvetica", 10),
            )
            self.score_canvas.create_rectangle(
                left,
                y,
                left + bar_width,
                y + 10,
                fill=color,
                outline=color,
            )
            self.score_canvas.create_text(
                left + bar_width + 6,
                y + 5,
                anchor="w",
                text=str(score).rstrip("0").rstrip("."),
                fill=TEXT,
                font=("Helvetica", 9),
            )

    def format_result(self, result: dict) -> str:
        markers = result.get("matched_text_markers") or []
        subject_markers = result.get("matched_subject_markers") or []
        links = result.get("links") or []
        attachments = result.get("attachments") or []

        lines = [
            f"Дата: {result.get('date', '')}",
            f"Кому: {result.get('recipient', '')}",
            f"Перемещение: {result.get('move_status', '')}",
            f"Куда: {result.get('moved_to', '')}",
            "",
            "Маркеры в теме:",
            ", ".join(subject_markers) or "нет",
            "",
            "Маркеры в тексте:",
            ", ".join(markers) or "нет",
            "",
            "Причина решения:",
            str(result.get("decision_reason", "")),
            "",
            "Ссылки:",
            ", ".join(links) or "нет",
            "",
            "Вложения:",
            ", ".join(attachments) or "нет",
            "",
            "Текст письма:",
            str(result.get("text", "")),
        ]

        return "\n".join(lines)


def main() -> int:
    base_dir = Path(__file__).parent

    if len(sys.argv) > 1:
        json_path = Path(sys.argv[1])
    else:
        json_path = base_dir / "classifier" / "result.json"

    root = tk.Tk()
    ResultViewer(root, json_path)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
