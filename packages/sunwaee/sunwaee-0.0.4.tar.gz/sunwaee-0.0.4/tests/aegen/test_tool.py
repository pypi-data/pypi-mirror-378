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
        assert tool.type == sample_tool["type"]
        assert tool.function.name == sample_tool["function"]["name"]
        assert tool.function.description == sample_tool["function"]["description"]
        assert (
            tool.function.parameters.properties["city"].model_dump()
            == sample_tool["function"]["parameters"]["properties"]["city"]
        )
        assert (
            tool.function.parameters.required
            == sample_tool["function"]["parameters"]["required"]
        )

    def test_tool_from_dict_missing_prop(self, sample_tool):
        tool = sample_tool.copy()
        tool["function"]["parameters"]["properties"] = {}
        with pytest.raises(ValueError, match="properties must be a non-empty dict"):
            Tool.from_dict(tool)

    def test_tool_from_list(self, sample_tools):
        tools = Tool.from_list(sample_tools)
        assert len(tools) == 2

        for idx, tool in enumerate(tools):
            assert tool.type == sample_tools[idx]["type"]
            assert tool.function.name == sample_tools[idx]["function"]["name"]
            assert (
                tool.function.description
                == sample_tools[idx]["function"]["description"]
            )
            assert (
                tool.function.parameters.model_dump()
                == sample_tools[idx]["function"]["parameters"]
            )
            assert (
                tool.function.parameters.required
                == sample_tools[idx]["function"]["parameters"]["required"]
            )
