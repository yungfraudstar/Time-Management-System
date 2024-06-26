import json
import math
from datetime import datetime

class TaskJuggler:
    """Eine Klasse zum Erstellen eines Zeitplans basierend auf Aufgaben und Ressourcen."""

    def __init__(self):
        """Initialisiert eine neue Instanz von TaskJuggler."""
        self.tasks = []
        self.resources = {}

    def load_data(self, tasks_file, resources_file):
        """Lädt Aufgaben- und Ressourcendaten aus JSON-Dateien.

        Args:
            tasks_file (str): Der Dateipfad zur Datei mit den Aufgabendaten.
            resources_file (str): Der Dateipfad zur Datei mit den Ressourcendaten.
        """
        try:
            with open(tasks_file, "r") as f:
                self.tasks = json.load(f)

            with open(resources_file, "r") as f:
                self.resources = json.load(f)

            self.tasks = sorted(self.tasks, key=lambda x: x.get("deadline", ""))
            self.tasks_order = [task["name"] for task in self.tasks]
        except FileNotFoundError as e:
            print(f"Fehler beim Laden der Daten: {e}")
            exit()

    def generate_schedule(self):
        """Generiert einen Zeitplan basierend auf den geladenen Aufgaben- und Ressourcendaten.

        Returns:
            dict: Ein Zeitplan mit zugewiesenen Aufgaben und Ressourcen.
        """
        schedule = {}

        for task in self.tasks:
            task_name = task.get("name")
            task_duration = task.get("duration")
            task_resources = task.get("resources")
            task_deadline = task.get("deadline")
            task_start_time = task.get("start_time")

            if not all([task_name, task_duration, task_resources, task_deadline, task_start_time]):
                print("Ungültige Aufgabe in der Datenquelle.")
                continue

            total_duration_needed = sum(task_duration for _ in task_resources)

            for resource_name in task_resources:
                if resource_name not in self.resources:
                    print(f"Unbekannte Ressource '{resource_name}' in der Aufgabe '{task_name}'.")
                    continue

                resource_data = self.resources[resource_name]
                resource_availability = resource_data["availability"]
                resource_plan_factor = resource_data.get("plan_factor", 1.0)
                resource_absence = resource_data.get("absence")

                # Berücksichtigung der Abwesenheit
                if resource_absence:
                    absence_start_date = datetime.strptime(resource_absence["start_date"], "%Y-%m-%d")
                    absence_end_date = datetime.strptime(resource_absence["end_date"], "%Y-%m-%d")
                    task_start_date = datetime.strptime(task_start_time, "%Y-%m-%d")

                    if absence_start_date <= task_start_date <= absence_end_date:
                        continue

                allocation_ratio = min(task_duration / total_duration_needed, resource_availability / total_duration_needed)
                allocated_duration = round(allocation_ratio * task_duration * resource_plan_factor, 2)

                if allocated_duration > 24:
                    days = math.ceil(allocated_duration / 24)
                    schedule.setdefault(task_name, {}).setdefault(resource_name, []).append((f"{days} days", task_start_time))
                else:
                    schedule.setdefault(task_name, {}).setdefault(resource_name, []).append((f"{allocated_duration} hours", task_start_time))

                self.resources[resource_name]["availability"] -= allocated_duration

        schedule["tasks_order"] = self.tasks_order

        return schedule

    def display_schedule(self, schedule):
        """Zeigt den generierten Zeitplan im Terminal an.

        Args:
            schedule (dict): Der generierte Zeitplan.
        """
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

if __name__ == "__main__":
    """Hauptskript zum Laden von Daten, Generieren eines Zeitplans und Anzeigen des Zeitplans."""
    task_juggler = TaskJuggler()

    task_juggler.load_data("tasks.json", "resources.json")

    schedule = task_juggler.generate_schedule()

    task_juggler.display_schedule(schedule)
