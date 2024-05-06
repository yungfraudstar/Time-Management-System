import json
import math

class TaskJuggler:
    def __init__(self):
        """Initialisiert eine Instanz von TaskJuggler."""
        self.tasks = []
        self.resources = {}

    def load_data(self, tasks_file, resources_file):
        """Lädt Aufgaben- und Ressourcendaten aus JSON-Dateien.

        Args:
            tasks_file (str): Der Dateipfad zur JSON-Datei mit den Aufgabendaten.
            resources_file (str): Der Dateipfad zur JSON-Datei mit den Ressourcendaten.
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
        """Generiert den Wochenzeitplan basierend auf den geladenen Daten.

        Returns:
            dict: Der Wochenzeitplan mit Aufgaben, Ressourcen und Zeiten.
        """
        schedule = {}
        for task in self.tasks:
            name, duration, resources, deadline, start_time = task.get("name"), task.get("duration"), task.get("resources"), task.get("deadline"), task.get("start_time")
            if not all([name, duration, resources, deadline, start_time]):
                print("Ungültige Aufgabe in der Datenquelle.")
                continue
            total_duration_needed = sum(duration for _ in resources)
            for resource_name in resources:
                if resource_name not in self.resources:
                    print(f"Unbekannte Ressource '{resource_name}' in der Aufgabe '{name}'.")
                    continue
                availability = self.resources[resource_name]["availability"]
                allocation_ratio = min(duration / total_duration_needed, availability / total_duration_needed)
                allocated_duration = round(allocation_ratio * duration, 2)
                if allocated_duration > 24:
                    days = math.ceil(allocated_duration / 24)
                    schedule.setdefault(name, {}).setdefault(resource_name, []).append((f"{days} days", start_time))
                else:
                    schedule.setdefault(name, {}).setdefault(resource_name, []).append((f"{allocated_duration} hours", start_time))
                self.resources[resource_name]["availability"] -= allocated_duration
        schedule["tasks_order"] = self.tasks_order
        return schedule

    def display_schedule(self, schedule):
        """Zeigt den Wochenzeitplan im Terminal an.

        Args:
            schedule (dict): Der zuvor generierte Wochenzeitplan.
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
    # Hauptskript
    task_juggler = TaskJuggler()

    # Daten laden
    task_juggler.load_data("tasks.json", "resources.json")

    # Zeitplan generieren
    schedule = task_juggler.generate_schedule()

    # Zeitplan anzeigen
    task_juggler.display_schedule(schedule)
