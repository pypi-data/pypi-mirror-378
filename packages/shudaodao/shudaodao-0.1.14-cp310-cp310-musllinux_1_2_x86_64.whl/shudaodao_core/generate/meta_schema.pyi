from dataclasses import dataclass

@dataclass
class InitFileTableModel:
    import_str: str
    router_str: str

@dataclass
class InitFileSchemaModel:
    router_path: str = ...
    imports: list[str] = ...
    routers: list[str] = ...
    def __init__(self, *, imports, routers, router_path) -> None: ...

class InitFileGenerateModel:
    imports: list[str]
