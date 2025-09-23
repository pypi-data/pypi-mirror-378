from ..schemas.query_request import Condition as Condition, QueryLogicOperation as QueryLogicOperation, QueryRequest as QueryRequest, QuerySimpleCondition as QuerySimpleCondition
from ..type.var import SQLModelDB as SQLModelDB, SQLModelResponse as SQLModelResponse
from .class_field import get_class_fields_with_sa_type as get_class_fields_with_sa_type
from sqlmodel import SQLModel as SQLModel
from typing import Any

class QueryBuilder:
    @classmethod
    def build_result(cls, selected_fields, results, model_class: type[SQLModelDB], response_class: type[SQLModelResponse] = None): ...
    @staticmethod
    def build_order_by(query: QueryRequest, model_class: type[SQLModel]) -> Any: ...
    @staticmethod
    def build_fields(query: QueryRequest, model_class: type[SQLModel]) -> Any: ...
    @staticmethod
    def build_where(condition: Condition, model_class: type[SQLModel]) -> Any: ...
