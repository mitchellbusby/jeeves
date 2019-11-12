import re

TAG_REGEX = "#([A-z]+)"

SPECIFIED_TIMEFRAME = "([0-9])+([dmh])"


def recall_parse(message):
    has_tags = re.findall(TAG_REGEX, message)

    if has_tags and len(has_tags) > 0:
        return {"type": "tag_search", "tags": has_tags}

    has_specified_timeframe = re.search(SPECIFIED_TIMEFRAME, message)

    if has_specified_timeframe:
        num, timeframe_type = has_specified_timeframe.groups()

        return {
            "type": "specified_timeframe_search",
            "number": int(num),
            "timeframe_type": timeframe_type,
        }

    return {"type": "default"}

