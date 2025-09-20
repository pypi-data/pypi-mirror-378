# standard
import typing

# third party
import pydantic

# custom


class Tool(pydantic.BaseModel):
    type: typing.Literal["function"] = "function"
    name: str
    description: str
    properties: dict[str, dict]
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

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": self.properties,
                    "required": self.required,
                },
            },
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Tool":
        func = data.get("function", {})
        params = func.get("parameters", {})
        return cls.model_validate(
            {
                "type": data.get("type", "function"),
                "name": func.get("name"),
                "description": func.get("description"),
                "properties": params.get("properties", {}),
                "required": params.get("required", []),
            }
        )

    @classmethod
    def from_list(cls, items: list[dict]) -> "list[Tool]":
        return [cls.from_dict(item) for item in items]
