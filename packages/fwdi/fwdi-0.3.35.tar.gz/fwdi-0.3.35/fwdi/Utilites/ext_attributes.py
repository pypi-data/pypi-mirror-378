from functools import wraps
from typing import Callable, Coroutine, TypeVar

T = TypeVar('T')
_C = TypeVar("_C", bound=Callable[..., Coroutine[None, None, T]])

class ExtAttr():

    @staticmethod     
    def set_attr(params:dict):
        def Inner(func:_C):
            func.__dict__['_attr'] = params
            return func
        return Inner
    
    @staticmethod
    def get_attr(func:Callable)->dict:
        if '_attr' in func.__dict__:
            return func.__dict__['_attr']