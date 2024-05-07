import json
import math
from datetime import datetime, timedelta

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

    def extend_task_duration(self, task_name, absent_user):
        """Verlängert die Dauer einer Aufgabe aufgrund der Abwesenheit eines Benutzers.

        Args:
            task_name (str): Der Name der Aufgabe, die verlängert werden soll.
            absent_user (str): Der Name des abwesenden Benutzers.

        Returns:
            bool: True, wenn die Aufgabe erfolgreich verlängert wurde, sonst False.
        """
        for task in self.tasks:
            if task["name"] == task_name:
                deadline = datetime.strptime(task["deadline"], "%Y-%m-%d")
                new_deadline = deadline + timedelta(days=1)  # Verlängern um einen Tag (Beispiel)
                task["deadline"] = new_deadline.strftime("%Y-%m-%d")
                return True
        print(f"Aufgabe '{task_name}' nicht gefunden.")
        return False

    def reallocate_resources(self, task_name, absent_user):
        """Neuverteilung der Ressourcen aufgrund der Abwesenheit eines Benutzers.

        Args:
            task_name (str): Der Name der Aufgabe, die neu zugewiesen werden soll.
            absent_user (str): Der Name des abwesenden Benutzers.

        Returns:
            bool: True, wenn die Ressourcen erfolgreich neu zugewiesen wurden, sonst False.
        """
        for task in self.tasks:
            if task["name"] == task_name:
                resources_needed = task["resources"]
                remaining_resources = [resource for resource in resources_needed if resource != absent_user]
                if remaining_resources:
                    task["resources"] = remaining_resources
                    return True
                else:
                    print("Keine verbleibenden Ressourcen für die Aufgabe.")
                    return False
        print(f"Aufgabe '{task_name}' nicht gefunden.")
        return False

if __name__ == "__main__":
    # Hauptskript
    task_juggler = TaskJuggler()

    # Daten laden
    task_juggler.load_data("tasks.json", "resources.json")

    # Zeitplan generieren
    schedule = task_juggler.generate_schedule()

    # Zeitplan anzeigen
    task_juggler.display_schedule(schedule)

    # Beispiel für die Anwendung der neuen Funktionen
    task_name = "Task1"
    absent_user = "Max"
    if task_juggler.extend_task_duration(task_name, absent_user):
        print(f"Aufgabe '{task_name}' wurde verlängert, da {absent_user} abwesend ist.")
    if task_juggler.reallocate_resources(task_name, absent_user):
        print(f"Ressourcen für Aufgabe '{task_name}' wurden neu zugewiesen aufgrund der Abwesenheit von {absent_user}.")
