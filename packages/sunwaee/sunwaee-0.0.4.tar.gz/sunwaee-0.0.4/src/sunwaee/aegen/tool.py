# standard
import typing

# third party
import pydantic

# custom


class Param(pydantic.BaseModel):
    type: str
    description: str


class Parameters(pydantic.BaseModel):
    type: str = "object"
    properties: dict[str, Param]
    required: list[str]

    @pydantic.field_validator("properties")
    @classmethod
    def check_properties_not_empty(cls, v):
        if not isinstance(v, dict) or not v:
            raise ValueError("properties must be a non-empty dict")
        return v

    @pydantic.field_validator("required", mode="before")
    @classmethod
    def check_required_in_properties(cls, v, info):
        properties = info.data.get("properties", {})
        for req in v:
            if req not in properties:
                raise ValueError(f"required field '{req}' not in properties")
        return v


class Function(pydantic.BaseModel):
    name: str
    description: str
    parameters: Parameters


class Tool(pydantic.BaseModel):
    type: typing.Literal["function"] = "function"
    function: Function

    @classmethod
    def from_dict(cls, data: dict) -> "Tool":
        func = data.get("function", {})
        params = func.get("parameters", {})
        return cls(
            function=Function(
                name=func["name"],
                description=func["description"],
                parameters=params,
            )
        )

    @classmethod
    def from_list(cls, items: list[dict]) -> "list[Tool]":
        return [cls.from_dict(item) for item in items]
