import pytest
from .parsers import recall_parse


class TestRecallParse:
    def test_recall_tags(self):
        message = "#mgmt"

        result = recall_parse(message)

        assert result["type"] == "tag_search"

        assert "mgmt" in result["tags"]

    def test_timeframe(self):
        message = "6m"

        result = recall_parse(message)

        assert result["type"] == "specified_timeframe_search"

        assert result["number"] == 6

        assert result["timeframe_type"] == "m"

    def test_default(self):

        message = ""

        result = recall_parse(message)

        assert result["type"] == "default"
