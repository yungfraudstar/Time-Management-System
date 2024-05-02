import tkinter as tk
from tkinter import messagebox, simpledialog
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np

class TeamManagementApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Team Management System")
        self.geometry("800x600")  # Fenstergröße anpassen
        
        self.tasks = {}  # Dictionary zum Speichern der Aufgaben

        self.user_name = simpledialog.askstring("Nutzername", "Geben Sie Ihren Namen ein:")

        # Widgets für die Hauptseite
        self.task_name_label = tk.Label(self, text="Aufgabenname:")
        self.task_name_label.pack()
        self.task_entry = tk.Entry(self)
        self.task_entry.pack()

        self.deadline_label = tk.Label(self, text="Deadline (DD.MM.YYYY):")
        self.deadline_label.pack()
        self.deadline_entry = tk.Entry(self)
        self.deadline_entry.pack()

        self.priority_label = tk.Label(self, text="Priorität:")
        self.priority_label.pack()
        self.priority_var = tk.StringVar(self)
        self.priority_var.set("Not important at all")
        self.priority_menu = tk.OptionMenu(self, self.priority_var, "Not important at all", "Not so important", "Still has time", "Important", "Very important")
        self.priority_menu.pack()

        self.add_task_button = tk.Button(self, text="Aufgabe hinzufügen", command=self.add_task)
        self.add_task_button.pack()

        self.task_listbox = tk.Listbox(self)
        self.task_listbox.pack()
        self.task_listbox.bind("<Double-Button-1>", self.show_task_details)

        self.update_priority_button = tk.Button(self, text="Priorität aktualisieren", command=self.update_priority)
        self.update_priority_button.pack()

        self.update_deadline_button = tk.Button(self, text="Deadline aktualisieren", command=self.update_deadline)
        self.update_deadline_button.pack()

        self.delete_task_button = tk.Button(self, text="Aufgabe löschen", command=self.delete_task)
        self.delete_task_button.pack()

        self.show_timeline_button = tk.Button(self, text="Zeitstrahl anzeigen", command=self.show_timeline)
        self.show_timeline_button.pack()

        # Aufgaben aus JSON-Datei laden
        self.load_tasks_from_json()

    def add_task(self):
        task_name = self.task_entry.get()
        deadline = self.deadline_entry.get()
        priority = self.priority_var.get()
        if task_name:
            # Überprüfen, ob die Deadline und Priorität eingegeben wurden
            if deadline:
                self.tasks[task_name] = {"deadline": deadline, "priority": priority, "assigned_to": self.user_name}
                self.save_tasks_to_json()
                self.update_task_listbox()
                messagebox.showinfo("Erfolg", "Aufgabe erfolgreich hinzugefügt!")
            else:
                messagebox.showerror("Fehler", "Bitte geben Sie die Deadline ein.")
        else:
            messagebox.showerror("Fehler", "Bitte geben Sie den Namen der Aufgabe ein.")

    def update_task_listbox(self):
        self.task_listbox.delete(0, tk.END)
        for task in self.tasks:
            self.task_listbox.insert(tk.END, task)

    def load_tasks_from_json(self):
        try:
            with open("tasks.json", "r") as f:
                self.tasks = json.load(f)
            self.update_task_listbox()
        except FileNotFoundError:
            pass  # Wenn die JSON-Datei noch nicht existiert, machen wir nichts

    def save_tasks_to_json(self):
        with open("tasks.json", "w") as f:
            json.dump(self.tasks, f)

    def show_task_details(self, event):
        selected_task_index = self.task_listbox.curselection()
        if selected_task_index:
            selected_task_name = self.task_listbox.get(selected_task_index)
            task_details = self.tasks[selected_task_name]
            deadline = task_details["deadline"]
            priority = task_details["priority"]
            assigned_to = task_details["assigned_to"]
            messagebox.showinfo("Aufgabendetails", f"Aufgabe: {selected_task_name}\nDeadline: {deadline}\nPriorität: {priority}\nZugewiesen an: {assigned_to}")

    def update_priority(self):
        selected_task_index = self.task_listbox.curselection()
        if selected_task_index:
            selected_task_name = self.task_listbox.get(selected_task_index)
            new_priority = simpledialog.askstring("Priorität aktualisieren", f"Aktuelle Priorität für {selected_task_name}: {self.tasks[selected_task_name]['priority']}\nNeue Priorität:")
            if new_priority:
                self.tasks[selected_task_name]["priority"] = new_priority
                self.save_tasks_to_json()
                self.update_task_listbox()
                messagebox.showinfo("Erfolg", "Priorität erfolgreich aktualisiert!")

    def update_deadline(self):
        selected_task_index = self.task_listbox.curselection()
        if selected_task_index:
            selected_task_name = self.task_listbox.get(selected_task_index)
            new_deadline = simpledialog.askstring("Deadline aktualisieren", f"Aktuelle Deadline für {selected_task_name}: {self.tasks[selected_task_name]['deadline']}\nNeue Deadline (DD.MM.YYYY):")
            if new_deadline:
                self.tasks[selected_task_name]["deadline"] = new_deadline
                self.save_tasks_to_json()
                self.update_task_listbox()
                messagebox.showinfo("Erfolg", "Deadline erfolgreich aktualisiert!")

    def delete_task(self):
        selected_task_index = self.task_listbox.curselection()
        if selected_task_index:
            selected_task_name = self.task_listbox.get(selected_task_index)
            confirm = messagebox.askyesno("Aufgabe löschen", f"Möchten Sie die Aufgabe '{selected_task_name}' wirklich löschen?")
            if confirm:
                del self.tasks[selected_task_name]
                self.save_tasks_to_json()
                self.update_task_listbox()
                messagebox.showinfo("Erfolg", "Aufgabe erfolgreich gelöscht!")

    def show_timeline(self):
        # Daten für den Zeitstrahl vorbereiten
        dates = []
        priorities = []
        tasks = []
        for task, details in self.tasks.items():
            deadline = datetime.strptime(details["deadline"], "%d.%m.%Y")  # Anpassung des Datumsformats
            dates.append(deadline)
            priorities.append(details["priority"])
            tasks.append(task)

        # Prioritäten in Werte konvertieren
        priority_mapping = {
            "Not important at all": 0.00,
            "Not so important": 0.25,
            "Still has time": 0.50,
            "Important": 0.75,
            "Very important": 1.00
        }
        priority_values = [priority_mapping[p] for p in priorities]

        # Zeitstrahl erstellen
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot_date(dates, priority_values, "-")

        # Beschriftungen hinzufügen (mit Prioritäten)
        for i, (txt, priority) in enumerate(zip(tasks, priorities)):
            ax.annotate(f"{txt} ({priority})", (dates[i], priority_values[i]), xytext=(-10, 0), textcoords="offset points", ha="right")

        # Achsen formatieren
        ax.xaxis_date()
        fig.autofmt_xdate()
        ax.set_xlabel("Deadline")
        ax.set_ylabel("Priorität")
        ax.set_yticks([0.00, 0.25, 0.50, 0.75, 1.00])  # Festlegen der Y-Achsen-Ticks
        ax.set_yticklabels(priority_mapping.keys())  # Verwenden der Prioritäten als Beschriftungen

        ax.set_title("Aufgaben Zeitstrahl")

        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    app = TeamManagementApp()
    app.mainloop()
