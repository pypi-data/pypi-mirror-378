# standard
import json

# third party
import pytest

# custom
from sunwaee.aegen.tool_call import ToolCall


@pytest.fixture
def sample_tool_call():
    return {
        "id": "tc_123",
        "type": "function",
        "function": {
            "name": "get_weather",
            "arguments": '{"city": "Paris"}',
        },
    }


class TestToolCall:

    def test_tool_call_from_dict(self, sample_tool_call):
        tool_call = ToolCall.from_dict(sample_tool_call)
        assert tool_call.id == "tc_123"
        assert tool_call.type == "function"
        assert tool_call.name == "get_weather"
        assert tool_call.arguments == {"city": "Paris"}

    def test_tool_call_from_dict_missing_id(self, sample_tool_call):
        inv = sample_tool_call.copy()
        inv.pop("id")

        with pytest.raises(ValueError, match="Tool call requires a non-empty 'id'"):
            ToolCall.from_dict(inv)

    def test_tool_call_from_dict_missing_function(self, sample_tool_call):
        inv = sample_tool_call.copy()
        inv.pop("function")

        with pytest.raises(
            ValueError,
            match="Tool call requires a 'function' object with 'name' and 'arguments'",
        ):
            ToolCall.from_dict(inv)

    def test_tool_call_from_dict_missing(self, sample_tool_call):
        inv = sample_tool_call.copy()
        inv["function"].pop("name")

        with pytest.raises(
            ValueError,
            match="Tool call 'function' requires a non-empty 'name'",
        ):
            ToolCall.from_dict(inv)

    def test_tool_call_from_dict_missing_arguments(self, sample_tool_call):
        inv = sample_tool_call.copy()
        inv["function"].pop("arguments")

        with pytest.raises(
            ValueError,
            match="Tool call 'function' requires 'arguments'",
        ):
            ToolCall.from_dict(inv)

    def test_tool_call_from_dict_invalid_arguments(self, sample_tool_call):
        inv = sample_tool_call.copy()
        inv["function"]["arguments"] = ["list", "of", "args"]

        with pytest.raises(
            ValueError,
            match="Tool call 'arguments' must be a JSON string or a dict",
        ):
            ToolCall.from_dict(inv)

    def test_tool_call_from_dict_invalid_json(self, sample_tool_call):
        inv = sample_tool_call.copy()
        inv["function"]["arguments"] = "invalid json"

        with pytest.raises(
            ValueError,
            match="Tool call 'arguments' string is not valid JSON",
        ):
            ToolCall.from_dict(inv)

    def test_tool_call_to_str(self, sample_tool_call):
        tool_call = ToolCall.from_dict(sample_tool_call)
        assert str(tool_call) == json.dumps(sample_tool_call, default=str)

    def test_tool_call_to_dict(self, sample_tool_call):
        tool_call = ToolCall.from_dict(sample_tool_call)
        assert tool_call.to_dict() == sample_tool_call
