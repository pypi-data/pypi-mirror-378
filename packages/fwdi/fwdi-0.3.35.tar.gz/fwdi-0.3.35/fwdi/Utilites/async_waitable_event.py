from asyncio import Event
from typing import TypeVar

T = TypeVar('T') 

class AsyncWaitableEvents(Event):
    def __init__(self) -> None:
        super().__init__()
        self.result:T = None
    
    def set(self, value:T) -> None:
        self.result = value
        self._loop.call_soon_threadsafe(super().set)
    
    async def wait(self)->T|None:
        await super().wait()
        
        return self.result