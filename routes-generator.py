import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import os
import re

class CSVEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Generator tras")
        self.root.geometry("800x605")

        self.cols = ["Lp", "Nazwa", "Audio", "Kierunek", "Extras"]
        self.stops_dictionary = self.load_dictionary()
        self.active_edit = None
        self.current_file_path = None
        
        info_frame = tk.LabelFrame(root, text="Metadane Trasy", padx=10, pady=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(info_frame, text="Operator:").grid(row=0, column=0, sticky="w")
        self.combo_operator = ttk.Combobox(info_frame, postcommand=self.update_operators)
        self.combo_operator.grid(row=0, column=1, padx=5, pady=2)
        self.combo_operator.bind("<<ComboboxSelected>>", lambda e: self.update_vehicle_types())

        tk.Label(info_frame, text="Typ pojazdu:").grid(row=0, column=2, sticky="w")
        self.combo_type = ttk.Combobox(info_frame)
        self.combo_type.grid(row=0, column=3, padx=5, pady=2)
        self.combo_type.bind("<<ComboboxSelected>>", lambda e: self.update_lines())

        tk.Label(info_frame, text="Linia:").grid(row=0, column=4, sticky="w")
        self.combo_line = ttk.Combobox(info_frame)
        self.combo_line.grid(row=0, column=5, padx=5, pady=2)

        tk.Label(info_frame, text="Kierunek:").grid(row=1, column=0, sticky="w")
        self.var_direction = tk.StringVar(value="-")
        tk.Label(info_frame, textvariable=self.var_direction, fg="blue", font=("Arial", 10, "bold")).grid(row=1, column=1, sticky="w")

        self.var_route_changed = tk.BooleanVar()
        tk.Checkbutton(info_frame, text="Zmiana trasy", variable=self.var_route_changed).grid(row=1, column=2, sticky="w")

        button_frame = tk.Frame(root)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(button_frame, text="Importuj CSV", command=self.import_csv).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Dodaj Przystanek", command=self.add_row).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Usuń Zaznaczone", command=self.delete_row, bg="#a01616", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Zapisz", command=self.quick_save, bg="#2C812F", fg="white").pack(side=tk.RIGHT, padx=5)
        tk.Button(button_frame, text="Zapisz jako...", command=self.save_csv, bg="#4C74AF", fg="white").pack(side=tk.RIGHT, padx=5)

        self.tree_frame = tk.Frame(root)
        self.tree_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)

        self.tree = ttk.Treeview(self.tree_frame, columns=self.cols, show='headings', selectmode="browse")
        for col in self.cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="w")
        self.tree.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)

        scroller = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroller.set)
        scroller.pack(side=tk.RIGHT, fill=tk.Y)

        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Edytuj komórkę", command=self.start_edit)
        self.context_menu.add_command(label="Usuń wiersz", command=self.delete_row)

        self.tree.bind("<Button-3>", self.show_context_menu)
        self.root.bind("<Button-1>", self.check_click_outside)
        self.root.bind("<Control-s>", lambda e: self.quick_save())
        self.root.bind("<Control-S>", lambda e: self.save_csv())
        self.root.bind("<Control-o>", lambda e: self.import_csv())

    def update_operators(self):
        base_path = "routes/"
        if os.path.exists(base_path):
            dirs = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
            self.combo_operator['values'] = sorted(dirs)

    def update_vehicle_types(self):
        op = self.combo_operator.get()
        base_path = f"routes/{op}"
        if op and os.path.exists(base_path):
            dirs = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
            self.combo_type['values'] = sorted(dirs)
            self.combo_type.set("")
            self.combo_line.set("")

    def update_lines(self):
        op = self.combo_operator.get()
        v_type = self.combo_type.get()
        base_path = f"routes/{op}/{v_type}"
        if op and v_type and os.path.exists(base_path):
            dirs = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
            self.combo_line['values'] = sorted(dirs)
            self.combo_line.set("")

    def refresh_direction(self):
        """Pobiera kierunek z pierwszej kolumny Kierunek w tabeli"""
        first_child = self.tree.get_children()
        if first_child:
            vals = self.tree.item(first_child[0])['values']
            if len(vals) > 3:
                self.var_direction.set(vals[3] if vals[3] else "BRAK")

    def load_dictionary(self):
        path = "dictionaries/stops.csv"
        return sorted(pd.read_csv(path, sep=';').iloc[:, 1].tolist()) if os.path.exists(path) else []

    def renumber_rows(self):
        for i, item in enumerate(self.tree.get_children(), 1):
            v = list(self.tree.item(item)['values'])
            v[0] = i
            self.tree.item(item, values=v)

    def clean_audio_text(self, t):
        return ' '.join(re.sub(r'\s\d{2}$', '', str(t)).replace("/", " ").split())

    def add_row(self, values=None):
        if values is None: values = ["" for _ in self.cols]
        self.tree.insert("", "end", values=values)
        self.renumber_rows()
        self.refresh_direction()

    def delete_row(self):
        selected = self.tree.selection()
        if selected and messagebox.askyesno("Usuwanie", "Usunąć zaznaczony przystanek?"):
            for item in selected: self.tree.delete(item)
            self.renumber_rows()

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.tree.focus(item)
            self.last_click_x, self.last_click_y = event.x, event.y
            self.context_menu.post(event.x_root, event.y_root)

    def start_edit(self, item_id=None, col_idx=None):
        self.close_active_edit()
        
        if item_id is None:
            item_id = self.tree.focus()
            column = self.tree.identify_column(self.last_click_x)
            col_idx = int(column[1:]) - 1
        
        if col_idx <= 0 or col_idx >= len(self.cols): return

        column_id = f"#{col_idx + 1}"
        vals = self.tree.item(item_id)['values']
        current_val = vals[col_idx] if len(vals) > col_idx else ""
        x, y, w, h = self.tree.bbox(item_id, column_id)

        self.active_edit = tk.Frame(self.tree) 
        self.active_edit.place(x=x, y=y, width=w, height=h)

        if col_idx == 1:
            entry = ttk.Combobox(self.active_edit, values=self.stops_dictionary)
            entry.set(current_val)
            entry.pack(fill=tk.BOTH)
            def filter_data(e):
                v = entry.get().lower()
                entry['values'] = self.stops_dictionary if v == '' else [s for s in self.stops_dictionary if v in s.lower()]
            entry.bind('<KeyRelease>', filter_data)
        else:
            entry = tk.Entry(self.active_edit)
            entry.insert(0, str(current_val))
            entry.pack(fill=tk.BOTH)

        entry.focus_set()

        def handle_navigation(event):
            new_val = entry.get()
            row_vals = list(self.tree.item(item_id)['values'])
            while len(row_vals) < len(self.cols): row_vals.append("")
            
            row_vals[col_idx] = new_val
            if col_idx == 1: row_vals[2] = self.clean_audio_text(new_val)
            
            self.tree.item(item_id, values=row_vals)
            self.refresh_direction()
            
            if event.keysym == 'Tab':
                self.close_active_edit()
                if event.state & 0x0001:
                    if col_idx > 1:
                        self.root.after(10, lambda: self.start_edit(item_id, col_idx - 1))
                else:
                    if col_idx < len(self.cols) - 1:
                        self.root.after(10, lambda: self.start_edit(item_id, col_idx + 1))
                return "break"
            
            elif event.keysym == 'Return':
                self.close_active_edit()
                return "break"
            
            elif event.keysym == 'Escape':
                self.close_active_edit()
                return "break"

        entry.bind("<Return>", handle_navigation)
        entry.bind("<Escape>", handle_navigation)
        entry.bind("<Tab>", handle_navigation)
        entry.bind("<Shift-Tab>", handle_navigation)

    def close_active_edit(self):
        if self.active_edit: self.active_edit.destroy(); self.active_edit = None

    def check_click_outside(self, event):
        if self.active_edit:
            t = event.widget
            while t:
                if t == self.active_edit: return
                t = t.master if hasattr(t, 'master') else None
            self.close_active_edit()

    def import_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if path:
            try:
                for i in self.tree.get_children(): self.tree.delete(i)
                df = pd.read_csv(path, sep=';', encoding='utf-8', comment='#').fillna("")
                for _, row in df.iterrows(): self.add_row(row.tolist())
                self.current_file_path = path
                self.refresh_direction()
            except Exception as e: messagebox.showerror("Błąd", str(e))
            
    def quick_save(self, event=None):
        if self.current_file_path: self._execute_save(self.current_file_path)
        else: self.save_csv()

    def save_csv(self, event=None):
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if path:
            self.current_file_path = path
            self._execute_save(path)

    def _execute_save(self, path):
        data = [self.tree.item(i)['values'] for i in self.tree.get_children()]
        if not data: return

        try:
            header = (
                "# Copyright:\n"
                "# (c) ROKMK 2026 - All rights reserved.\n"
                "# Generated with Routes-Generator for SIP by ROKMK.\n#\n"
                "# Route Info:\n"
                f"# Line: {self.combo_line.get()}   Direction: {self.var_direction.get()}   "
                f"Stops amount: {len(data)}   Route changed: {self.var_route_changed.get()}\n"
                f"# Line operator: {self.combo_operator.get()}   Vehicle type: {self.combo_type.get()}\n"
            )

            with open(path, 'w', encoding='utf-8') as f:
                f.write(header)
            
            df = pd.DataFrame(data, columns=self.cols)
            df.to_csv(path, sep=';', index=False, encoding='utf-8', mode='a')

            with open(path, 'a', encoding='utf-8') as f:
                f.write(f"# Generated at {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

            messagebox.showinfo("Sukces", "Zapisano z metadanymi!")
        except Exception as e:
            messagebox.showerror("Błąd", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVEditor(root)
    root.mainloop()