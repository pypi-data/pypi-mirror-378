from typing import Any, overload
from contextlib import asynccontextmanager
from fastmcp import Client
from mcp.types import CallToolResult, GetPromptResult, TextResourceContents, BlobResourceContents
from ...Application.Abstractions.External.base_mcp_client import BaseMCPClient

class MCPClient(BaseMCPClient):
    def __init__(self, api_key:str|None=None, host:str='127.0.0.1', port:int=6504, path:str='mcp'):
        super().__init__()
        self.__base_url:str = f"http://{host}:{port}/{path}"

        if api_key:
            self.__client:Client = Client(self.__base_url, auth=api_key)
        else:
            self.__client:Client = Client(self.__base_url)

    @classmethod
    def create_from_url(cls, url:str, api_key:str|None=None):
        if hasattr(MCPClient, '__log__'):
            MCPClient.__log__(f"Creating mcp client:{url}")
        else:
            print(f"DEBUG::Creating mcp client:{url}")

        instance = cls()
        instance.__base_url = url
        if api_key:
            instance.__client = Client(url, auth=api_key)
        else:
            instance.__client = Client(url)

    async def check_avaible(self):
        return True if await self.__client.ping() else False
    
    async def load_env(self)->bool:
        if hasattr(MCPClient, '__log__'):
            MCPClient.__log__(f"Environment loading mcp client:{self.__base_url}")
        else:
            print(f"DEBUG::Environment loading mcp client:{self.__base_url}")            
        try:
            async with self.__client as client:
                self.tools = await client.list_tools()
                self.prompts = await client.list_prompts()
                self.resources = await client.list_resources()
                
                return True
            
            return False
        except Exception as ex:
            print(f"ERROR:{ex}")
            return False
    
    @property
    def is_connected(self)->bool:
        return self.__client.is_connected()

    async def ping(self)->bool:
        async with self.__client as client:
            result = await client.ping()
            return result

    async def call_tool(self, name_fn:str, param:dict[str, Any]=None)->CallToolResult:
        if hasattr(MCPClient, '__log__'):
            MCPClient.__log__(f"call_tool:{name_fn}, {param}", 'debug')
        else:
            print(f"DEBUG::call_tool:{name_fn}, {param}")            

        async with self.__client as client:
            if param:
                result = await client.call_tool(name_fn, param)
            else:
                result = await client.call_tool(name_fn)

        return result

    async def read_resource(self, uri:str)->list[TextResourceContents | BlobResourceContents]:
        if hasattr(MCPClient, '__log__'):
            MCPClient.__log__(f"read_resource:{uri}", 'debug')
        else:
            print(f"DEBUG::ead_resource:{uri}")              
        async with self.__client as client:
            result = await client.read_resource(uri)

            return result
        return []

    async def get_prompt(self, name:str, param:dict[str, Any]=None)->GetPromptResult:
        if hasattr(MCPClient, '__log__'):
            MCPClient.__log__(f"get_prompt:{name}, {param}", 'debug')
        else:
            print(f"get_prompt:{name}, {param}")              

        async with self.__client as client:
            if param:
                result = await client.get_prompt(name, arguments=param)
            else:
                result = await client.get_prompt(name)

        return result