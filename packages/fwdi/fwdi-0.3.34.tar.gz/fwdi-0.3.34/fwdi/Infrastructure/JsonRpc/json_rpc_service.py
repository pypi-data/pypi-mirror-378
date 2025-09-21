from types import FunctionType
from typing import Union
from collections.abc import Coroutine

from fastapi_jsonrpc import Entrypoint
from fastapi import FastAPI

class JRPCService():
    def __init__(self, path:str='/api/v1/jsonrpc'):
        self.__entrypoint = Entrypoint(path=path)
    
    def add_method(self, 
                   func: Union[FunctionType, Coroutine],
                   name:str|None=None):
        try:
            if name:
                self.__entrypoint.add_method_route(func=func, name=name)
            else:
                self.__entrypoint.add_method_route(func=func)
                
        except Exception as ex:
            print(f"ERROR:{ex}")
    
    def mount_to_asgi(self, fast_api:FastAPI, path:str='rpc'):
        fast_api.mount(path, self.__entrypoint)