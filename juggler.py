import json

class TaskJuggler:
    def __init__(self):
        self.tasks = []
        self.resources = {}

    def load_data(self, tasks_file, resources_file):
        # Aufgaben aus JSON-Datei laden
        with open(tasks_file, "r") as f:
            self.tasks = json.load(f)

        # Ressourcen aus JSON-Datei laden
        with open(resources_file, "r") as f:
            self.resources = json.load(f)

    def generate_schedule(self):
        schedule = {}

        # Für jede Aufgabe die entsprechenden Mitarbeiter finden und dem Zeitplan hinzufügen
        for task in self.tasks:
            task_name = task["name"]
            task_duration = task["duration"]
            task_resources = task["resources"]
            schedule[task_name] = {}

            total_duration_needed = sum(task_duration for _ in task_resources)
            for resource_name in task_resources:
                if resource_name in self.resources:
                    resource_availability = self.resources[resource_name]["availability"]
                    allocation_ratio = min(task_duration / total_duration_needed, resource_availability / total_duration_needed)
                    schedule[task_name][resource_name] = round(allocation_ratio * task_duration, 2)
                    self.resources[resource_name]["availability"] -= round(allocation_ratio * task_duration, 2)

        return schedule

    def export_schedule(self, schedule, output_file):
        with open(output_file, "w") as f:
            json.dump(schedule, f, indent=4)

if __name__ == "__main__":
    # TaskJuggler-Instanz erstellen
    task_juggler = TaskJuggler()

    # Daten laden
    task_juggler.load_data("tasks.json", "resources.json")

    # Zeitplan generieren
    schedule = task_juggler.generate_schedule()

    # Zeitplan exportieren (als JSON-Datei)
    task_juggler.export_schedule(schedule, "schedule.json")

    # Zeitplan exportieren (als TXT-Datei)
    with open("schedule.txt", "w") as f:
        for task, resources in schedule.items():
            f.write(f"{task}:\n")
            for resource, duration in resources.items():
                f.write(f"\t{resource}: {duration} hours\n")
