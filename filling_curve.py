import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
import csv
import locale

class FillingCurveApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Filling-curve calculator")
        self.geometry("800x700")

        # Detect language before creating widgets
        self.default_language = self.detect_language()

        self.create_widgets()

    def create_widgets(self):
        params = [
            ("Vessel type", ["Vertical Tank", "Horizontal Tank"]),
            ("Head type", ["Torospherical Head (DIN 28011)", "Torospherical Head (DIN 28013)"]),
            ("Outer diameter (mm)", ""),
            ("Wall thickness (mm)", ""),
            ("Length (mm)", "")
        ]

        self.entries = {}
        row = 0
        for label, default in params:
            tk.Label(self, text=label).grid(row=row, column=0, sticky="w", padx=10, pady=5)
            if isinstance(default, list):
                cb = ttk.Combobox(self, values=default, state="readonly")
                cb.current(0)
                cb.grid(row=row, column=1, sticky="ew", padx=10)
                self.entries[label] = cb
            else:
                ent = tk.Entry(self)
                ent.grid(row=row, column=1, sticky="ew", padx=10)
                ent.insert(0, str(default))
                self.entries[label] = ent
            row += 1

        # Calculate Button
        btn = tk.Button(self, text="Calculate", command=self.calculate)
        btn.grid(row=row, column=0, sticky="w", pady=10, padx=10)

        # Progressbar Label and Progressbar
        self.progress_label = tk.Label(self, text="Progress")
        self.progress_label.grid(row=row, column=1, sticky="w", padx=5)
        self.progress = ttk.Progressbar(self, orient="horizontal", length=200, mode="determinate")
        self.progress.grid(row=row, column=1, sticky="w", padx=5)
        self.progress.grid_remove()  # initially hide
        self.progress_label.grid_remove()

        row += 1  # next row

        # Export Button
        btn_export = tk.Button(self, text="Export (CSV)", command=self.export_csv)
        btn_export.grid(row=row, column=0, sticky="w", pady=10, padx=10)

        # Treeview and Scrollbar
        self.tree = ttk.Treeview(self, columns=("level_cm", "volume_m³"), show="headings", height=20)
        self.tree.heading("level_cm", text="Level (cm)")
        self.tree.heading("volume_m³", text="Volume (m³)")
        self.tree.grid(row=row+1, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=row+1, column=4, sticky="ns")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(row+1, weight=1)


    def calculate(self):
        vessel_type = self.entries["Vessel type"].get()
        head_type = self.entries["Head type"].get()

        if vessel_type not in ["Vertical Tank", "Horizontal Tank"]:
            messagebox.showerror("Error", "Please select a valid vessel type!")
            return

        if head_type not in ["Torospherical Head (DIN 28011)", "Torospherical Head (DIN 28013)"]:
            messagebox.showerror("Error", "Please select a valid head type!")
            return

        try:
            da = float(self.entries["Outer diameter (mm)"].get())
            s = float(self.entries["Wall thickness (mm)"].get())
            L = float(self.entries["Length (mm)"].get())
        except ValueError:
            messagebox.showerror("Error", "Please check you input parameters!")
            return

        if head_type == "Torospherical Head (DIN 28011)":
            r1 = 1 * da
            r2 = 0.1 * da
            h2 = 0.1935 * da + 0.455 * s
        else:
            r1 = 0.8 * da
            r2 = 0.154 * da
            h2 = 0.255 * da + 0.635 * s

        if vessel_type == "Vertical Tank":
            # hide progressbar
            self.progress.grid_remove()
            self.progress_label.grid_remove()

            result = self.calculate_vertical(da, s, r1, r2, h2, L)
        else:
            # show progressbar
            self.progress_label.grid()
            self.progress.grid()
            self.progress['value'] = 0
            self.update_idletasks()

            result = self.calculate_horizontal(da, s, r1, r2, h2, L)

            # Progressbar am Ende ausblenden
            self.progress.grid_remove()
            self.progress_label.grid_remove()

        self.show_result(result)

    def calculate_vertical(self, da, s, r1, r2, h2, L):
        alpha = (r1 - h2) / (r1 - r2)
        x1 = h2 - r2 * math.sin(alpha)
        x2 = h2
        x3 = L - s - h2
        x4 = L - s - x1

        V = 0
        result = []

        def radius(x):
            if 0 <= x < x1:
                return math.sqrt(r1**2 - (x - r1)**2)
            elif x1 <= x < x2:
                a = 1
                b = -2 * (da / 2 - s - r2)
                c = (da / 2 - s - r2)**2 + (x - x2)**2 - r2**2
                disc = b**2 - 4*a*c
                return (-b + math.sqrt(disc)) / (2*a) if disc >= 0 else 0
            elif x2 <= x < x3:
                return da / 2 - s
            elif x3 <= x < x4:
                a = 1
                b = -2 * (da / 2 - s - r2)
                c = (da / 2 - s - r2)**2 + (x - x3)**2 - r2**2
                disc = b**2 - 4*a*c
                return (-b + math.sqrt(disc)) / (2*a) if disc >= 0 else 0
            elif x4 < x <= L:
                return math.sqrt(r1**2 - (x - (L - s - r1))**2)
            else:
                return 0

        for i in range(int(L - 2*s) + 1):
            fx = radius(i)**2
            fx1 = radius(i+1)**2
            V += math.pi * 0.5 * (fx + fx1) * 1e-9  # Volumen in m³

            if i % 10 == 0:
                result.append((
                    i / 10,   # Höhe cm
                    V         # Volumen m³
                ))

        return result

    def cross_section(self, z, xmin, xmax, dx, da, s, r1, r2, h2, L):
        alpha = (r1 - h2) / (r1 - r2)
        x1 = h2 - r2 * math.sin(alpha)
        x2 = h2
        x3 = L - s - h2
        x4 = L - s - x1

        def radius(x):
            if 0 <= x < x1:
                return math.sqrt(r1**2 - (x - r1)**2)
            elif x1 <= x < x2:
                a = 1
                b = -2 * (da / 2 - s - r2)
                c = (da / 2 - s - r2)**2 + (x - x2)**2 - r2**2
                disc = b**2 - 4*a*c
                return (-b + math.sqrt(disc)) / (2*a) if disc >= 0 else 0
            elif x2 <= x < x3:
                return da / 2 - s
            elif x3 <= x < x4:
                a = 1
                b = -2 * (da / 2 - s - r2)
                c = (da / 2 - s - r2)**2 + (x - x3)**2 - r2**2
                disc = b**2 - 4*a*c
                return (-b + math.sqrt(disc)) / (2*a) if disc >= 0 else 0
            elif x4 < x <= L:
                return math.sqrt(r1**2 - (x - (L - s - r1))**2)
            else:
                return 0

        area = 0
        steps = int((xmax - xmin) / dx) + 1
        for i in range(steps):
            x = xmin + i * dx
            R = radius(x)
            if z**2 <= R**2:
                height = 2 * math.sqrt(R**2 - z**2)
            else:
                height = 0
            area += height * dx
        return area

    def calculate_horizontal(self, da, s, r1, r2, h2, L):
        dx = 1
        dz = 1
        V = 0
        result = []

        x_min = 0
        x_max = L - 2 * s

        z_min = int(-1 * (da / 2 - s))
        z_max = int(da / 2 - s)

        steps = (z_max - z_min) // dz + 1

        for idx, z in enumerate(range(z_min, z_max + 1, dz)):
            A = self.cross_section(z, x_min, x_max, dx, da, s, r1, r2, h2, L)
            V += A * dz * 1e-9
            level = z + (da / 2 - s)

            if idx % 10 == 0:
                result.append((
                    level / 10,
                    V
                ))

            # update Progressbar
            progress_value = (idx + 1) / steps * 100
            self.progress['value'] = progress_value
            self.update_idletasks()

        return result

    def show_result(self, data):
        self.tree.delete(*self.tree.get_children())
        for row in data:
            self.tree.insert("", "end", values=(
                f"{int(round(row[0]))}",    # Level (cm)
                f"{row[1]:.2f}"            # Volume (m³)
            ))

    def export_csv(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save result as CSV"
        )
        if not filepath:
            return

        try:
            is_german = (self.default_language == "Deutsch")  # Detect language

            with open(filepath, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow(["Level (cm)", "Volume (m3)"])
                for child in self.tree.get_children():
                    row = self.tree.item(child)['values']
                    level = str(row[0]) 
                    volume = str(row[1])
                    if is_german:
                        volume = volume.replace('.', ',')
                    writer.writerow([level, volume])

            messagebox.showinfo("Success", f"File successfully saved:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Saving failed:\n{e}")
            
    def detect_language(self):
        # Get system language setting, e.g. 'de_DE', 'en_US', etc.
        lang_code = locale.getdefaultlocale()[0]

        if lang_code and lang_code.startswith("de"):
            return "Deutsch"
        else:
            return "English"
        


if __name__ == "__main__":
    app = FillingCurveApp()
    app.mainloop()
