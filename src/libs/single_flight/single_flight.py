from typing import Dict
from src.libs.single_flight.dto import Status, Task




class SingleFlight:

    def __init__(self):
        self.tasks_status: Dict[int, Task] = {}

    def add_task(self, task_id: int, name: str):
        if self.doing_task():
            return False
        self.tasks_status[task_id] = Task(name=name)
        return True

    def finish_task(self, task_id: int):
        self.tasks_status[task_id].status = Status.finished

    def get_task(self, task_id: int):
        return self.tasks_status[task_id].status

    def get_doing_task(self):
        for task in self.tasks_status.values():
            if task.status == Status.processing or task.status == Status.started:
                return task
        return None

    def doing_task(self):
        return any(True for task in self.tasks_status.values() if task.status == Status.started or task.status == Status.processing)
