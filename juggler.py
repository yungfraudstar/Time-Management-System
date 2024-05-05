# Importieren der benötigten Module
import json
import math

# Definition der Klasse TaskJuggler
class TaskJuggler:
    # Initialisierung der Klasse
    def __init__(self):
        # Initialisierung der Attribute
        self.tasks = []             # List für Aufgaben
        self.resources = {}        # Dictionary für Ressourcen
        self.plan_factor = 1.0     # Initialer Planfaktohr

    # Laden der Daten aus JSON-Dateien
    def load_data(self, tasks_file, resources_file):
        try:
            # Laden der Aufgaben aus der JSON-Datei
            with open(tasks_file, "r") as f:
                self.tasks = json.load(f)

            # Laden der Ressourcen aus der JSON-Datei
            with open(resources_file, "r") as f:
                self.resources = json.load(f)

            # Sortieren der Aufgaben nach ihrer Deadline und Speichern der Reihenfolge
            self.tasks = sorted(self.tasks, key=lambda x: x.get("deadline", ""))
            self.tasks_order = [task["name"] for task in self.tasks]
        except FileNotFoundError as e:
            print(f"Fehler beem Laden der Daten: {e}")
            exit()

    # Generieren des Zeitplans unter Berücksichtigung des Planfaktohrs
    def generate_schedule(self):
        schedule = {}  # Initialisierung des Zeitplans

        # Iteration über alle Aufgaben
        for task in self.tasks:
            task_name = task.get("name")
            task_duration = task.get("duration") * self.plan_factor  # Anpassung der Dauer mit dem Planfaktohr
            task_resources = task.get("resources")
            task_deadline = task.get("deadline")
            task_start_time = task.get("start_time")

            # Überprüfen, ob alle benötigten Informationen vorhanden sind
            if not all([task_name, task_duration, task_resources, task_deadline, task_start_time]):
                print("Ungültige Aufgabe in der Datenquelle.")
                continue

            # Berechnung der Gesamtdauer, die für die Aufgabe benötigt wird
            total_duration_needed = sum(task_duration for _ in task_resources)

            # Iteration über alle Ressourcen, die für die Aufgabe benötigt werden
            for resource_name in task_resources:
                if resource_name not in self.resources:
                    print(f"Unbekannte Ressource '{resource_name}' in der Aufgabe '{task_name}'.")
                    continue

                resource_availability = self.resources[resource_name]["availability"]
                # Berechnung des Anteils der Ressource an der Gesamtdauer
                allocation_ratio = min(task_duration / total_duration_needed, resource_availability / total_duration_needed)
                # Berechnung der zugeteilten Dauer für die Ressource
                allocated_duration = round(allocation_ratio * task_duration, 2)

                # Aufteilen der Arbeitszeit in Stunden oder Tage, je nach Bedarf
                if allocated_duration > 24:
                    days = math.ceil(allocated_duration / 24)
                    schedule.setdefault(task_name, {}).setdefault(resource_name, []).append((f"{days} days", task_start_time))
                else:
                    schedule.setdefault(task_name, {}).setdefault(resource_name, []).append((f"{allocated_duration} hours", task_start_time))
                # Aktualisieren der Verfügbarkeit der Ressource
                self.resources[resource_name]["availability"] -= allocated_duration

        # Hinzufügen der Reihenfolge der Aufgaben zum Zeitplan
        schedule["tasks_order"] = self.tasks_order

        return schedule

    # Anzeigen des Zeitplans im Terminal
    def display_schedule(self, schedule):
        print("\033[1mWeekly Schedule:\033[0m")
        for task, resources in schedule.items():
            if task == "tasks_order":
                continue
            print("\033[1mTask:\033[0m", task)
            if isinstance(resources, dict):
                for resource, durations in resources.items():
                    for duration, start_time in durations:
                        print("\t\033[1mResource:\033[0m", resource)
                        print("\t\t\033[1mDuration:\033[0m", duration)
                        print("\t\t\033[1mStart Time:\033[0m", start_time)
            else:
                print("\t\033[1mNo assigned resources.\033[0m")
        
        tasks_order = schedule.get("tasks_order")
        if tasks_order:
            print("\n\033[1mTask Deadlines:\033[0m")
            for task_name in tasks_order:
                task = next((t for t in self.tasks if t["name"] == task_name), None)
                if task:
                    print(f"\tTask: {task_name}, Deadline: {task.get('deadline')}")

    # Setzen des Planfaktohrs
    def set_plan_factor(self, factor):
        self.plan_factor = factor

# Hauptfunktion des Scripts
if __name__ == "__main__":
    # Erstellen einer TaskJuggler-Instanz
    task_juggler = TaskJuggler()

    # Laden der Daten aus den JSON-Dateien
    task_juggler.load_data("tasks.json", "resources.json")

    # Hier wird der Planfaktohr auf 1 gesetzt
    task_juggler.set_plan_factor(1)

    # Generieren des Zeitplans
    schedule = task_juggler.generate_schedule()

    # Anzeigen des Zeitplans
    task_juggler.display_schedule(schedule)
