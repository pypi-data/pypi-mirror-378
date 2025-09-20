# standard
# third party
import pytest

# custom
from sunwaee.aegen.tool import Tool


@pytest.fixture
def sample_tool():
    return {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "The city (e.g. Paris, London...)",
                    },
                },
                "required": ["city"],
            },
        },
    }


@pytest.fixture
def sample_tools():
    return [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get weather.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "The city (e.g. Paris, London...)",
                        },
                    },
                    "required": ["city"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_hour",
                "description": "Get hour.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "timezone": {
                            "type": "string",
                            "description": "The timezone (e.g. Paris, London...)",
                        },
                    },
                    "required": ["timezone"],
                },
            },
        },
    ]


class TestTool:

    def test_tool_from_dict(self, sample_tool):
        tool = Tool.from_dict(sample_tool)
        assert tool.type == "function"
        assert tool.name == "get_weather"
        assert tool.description == "Get weather."
        assert tool.properties == {
            "city": {
                "type": "string",
                "description": "The city (e.g. Paris, London...)",
            },
        }
        assert tool.required == ["city"]

    def test_tool_from_dict_invalid_props(self):
        tool = {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get weather.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": ["city"],
                },
            },
        }

        with pytest.raises(ValueError, match="properties must be a non-empty dict"):
            Tool.from_dict(tool)

    def test_tool_from_list(self, sample_tools):
        tools = Tool.from_list(sample_tools)
        assert len(tools) == 2

        assert tools[0].type == "function"
        assert tools[0].name == "get_weather"
        assert tools[0].description == "Get weather."
        assert tools[0].properties == {
            "city": {
                "type": "string",
                "description": "The city (e.g. Paris, London...)",
            },
        }
        assert tools[0].required == ["city"]

        assert tools[1].type == "function"
        assert tools[1].name == "get_hour"
        assert tools[1].description == "Get hour."
        assert tools[1].properties == {
            "timezone": {
                "type": "string",
                "description": "The timezone (e.g. Paris, London...)",
            },
        }
        assert tools[1].required == ["timezone"]

    def test_tool_to_dict(self, sample_tool):
        tool = Tool.from_dict(sample_tool)
        assert tool.to_dict() == sample_tool
