from asyncio import new_event_loop, AbstractEventLoop, set_event_loop
import threading
from ..Abstractions.External.base_task_queue_manager import BaseTaskQueueManager
from ...Application.TaskManager.job_task import JobTask
from ...Application.TaskManager.task_queue_item import TaskQueueItem

class TaskQueueManager(BaseTaskQueueManager):
    def __init__(self) -> None:
        super().__init__()
        self.__pull_queue:dict[str, TaskQueueItem] = {}
        self.__loop:AbstractEventLoop|None = None
        self.add_queue('main')
    
    def create_loop(self):
        self.__loop = new_event_loop()
        thread = threading.Thread(target=self.__run_event_loop, args=(self.__loop,), daemon=True)
        thread.start()

    def __run_event_loop(self, loop):
        set_event_loop(loop)
        loop.run_forever()

    def queue_exists(self, name:str)->bool:
        return True if name in self.__pull_queue else False

    def add_queue(self, name:str)->TaskQueueItem | None:
        TaskQueueManager.__log__(f"add_queue:{name}", 'debug')
        try:
            if not name in self.__pull_queue:
                if not self.__loop:
                    self.create_loop()
                self.__pull_queue[name] = TaskQueueItem(self.__loop)
                self.__pull_queue[name].start()

            return self.__pull_queue[name]        
        except Exception as ex:
            TaskQueueManager.__log__(ex, 'error')
            return None

    def check_task_id(self, pull_name:str, task_id:str)->int:
        if self.queue_exists(pull_name):
            return self.__pull_queue[pull_name].check_task(task_id)

    def add_task(self, task: JobTask, pull_name:str='main')->JobTask | None:
        TaskQueueManager.__log__(f"add_task:{task.id}, pull name:{pull_name}", 'debug')

        try:
            if self.queue_exists(pull_name):
                return self.__pull_queue[pull_name].add(task)
            else:
                TaskQueueManager.__log__(f"Error::Task pull is not exists!", 'error')
                raise Exception(f"Error::Task pull is not exists!")

        except Exception as ex:
            TaskQueueManager.__log__(ex, 'error')
            return None