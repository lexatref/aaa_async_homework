import abc
import asyncio
from typing import Coroutine, Any

"""
Описание задачи:
    Необходимо реализовать планировщик, позволяющий запускать и отслеживать фоновые корутины.
    Планировщик должен обеспечивать:
        - возможность планирования новой задачи
        - отслеживание состояния завершенных задач (сохранение результатов их выполнения)
        - отмену незавершенных задач перед остановкой работы планировщика
        
    Ниже представлен интерфейс, которому должна соответствовать ваша реализация.
    
    Обратите внимание, что перед завершением работы планировщика, все запущенные им корутины должны быть
    корректным образом завершены.
    
    В папке tests вы найдете тесты, с помощью которых мы будем проверять работоспособность вашей реализации
    
"""


class AbstractRegistrator(abc.ABC):
    """
    Сохраняет результаты работы завершенных задач.
    В тестах мы передадим в ваш Watcher нашу реализацию Registrator и проверим корректность сохранения результатов.
    """

    @abc.abstractmethod
    def register_value(self, value: Any) -> None:
        # Store values returned from done task
        ...

    @abc.abstractmethod
    def register_error(self, error: BaseException) -> None:
        # Store exceptions returned from done task
        ...


class AbstractWatcher(abc.ABC):
    """
    Абстрактный интерфейс, которому должна соответсововать ваша реализация Watcher.
    При тестировании мы расчитываем на то, что этот интерфейс будет соблюден.
    """

    def __init__(self, registrator: AbstractRegistrator):
        self.registrator = registrator  # we expect to find registrator here

    @abc.abstractmethod
    async def start(self) -> None:
        # Good idea is to implement here all necessary for start watcher :)
        ...

    @abc.abstractmethod
    async def stop(self) -> None:
        # Method will be called on the end of the Watcher's work
        ...

    @abc.abstractmethod
    def start_and_watch(self, coro: Coroutine) -> None:
        # Start new task and put to watching
        ...


class StudentWatcher(AbstractWatcher):
    def __init__(self, registrator: AbstractRegistrator):
        super().__init__(registrator)
        # Your code goes here
        self.started_tasks = set()

    async def start(self) -> None:
        # Your code goes here
        self.started_tasks.clear()
        task = asyncio.create_task(StudentWatcher.watch(self))
        self.watcher = task
        await asyncio.sleep(0)

    async def stop(self) -> None:
        #Your code goes here
        await asyncio.sleep(1)
        canceled_tasks = []
        tasks = asyncio.all_tasks()
        for t in tasks:
            if t in self.started_tasks:
                res = t.cancel()
                print(res)
                canceled_tasks.append(t)
        await asyncio.gather(*canceled_tasks, return_exceptions=True)
        self.watcher.cancel()
        await asyncio.gather(self.watcher, return_exceptions=True)


    def start_and_watch(self, coro: Coroutine) -> None:
        # Your code goes here
        task = asyncio.create_task(coro)
        self.started_tasks.add(task)

    @staticmethod
    async def watch(class_ex):
        while True:
            tasks_done = set()
            for t in class_ex.started_tasks:
                if t.done():
                    try:
                        res = t.result()
                        class_ex.registrator.register_value(res)
                    except:
                        res = t.exception()
                        class_ex.registrator.register_error(res)
                    tasks_done.add(t)
            class_ex.started_tasks = class_ex.started_tasks - tasks_done
            await asyncio.sleep(.1)