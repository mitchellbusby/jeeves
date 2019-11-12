import datetime
import uuid
from urllib.parse import parse_qs

import arrow
from chalice import Chalice
from chalicelib.reflection_model import ReflectionModel
from chalicelib.decorators import requires_user_id
from chalicelib.parsers import recall_parse


app = Chalice(app_name="jeeves")


@app.route("/")
def index():
    # Simple uptime check :grin:
    return {"hello": "world"}


@app.route(
    "/reflect", methods=["POST"], content_types=["application/x-www-form-urlencoded"]
)
@requires_user_id(app)
def reflect():
    parsed = parse_qs(app.current_request.raw_body.decode())

    message = parsed.get("text")

    reflect = message[0]

    if ReflectionModel.exists():
        persist_reflection(reflect)

    return f"You reflected: {reflect}"


@app.route(
    "/recall", methods=["POST"], content_types=["application/x-www-form-urlencoded"]
)
@requires_user_id(app)
def recall():
    parsed = parse_qs(app.current_request.raw_body.decode())
    message = parsed.get("text")[0]

    unpacked = recall_parse(message)

    if unpacked["type"] == "tag_search":
        return "Sorry, haven't implemented that one yet~"

    # Default is 7 days
    delta = datetime.timedelta(days=7)

    if unpacked["type"] == "specified_timeframe_search":
        delta = get_delta_from_parsed_recall(unpacked)

    start_date = datetime.datetime.utcnow() - delta

    results = ReflectionModel.scan(
        filter_condition=ReflectionModel.creation_time_utc > start_date
    )

    sort_fn = lambda x: x.creation_time_utc

    results = sorted(list(results), key=sort_fn, reverse=True)

    if len(results) == 0:
        return "Sorry, there were no reflections for the timeframe you specified! 😅"

    string = ""

    for result in results:
        humanized_time = arrow.get(result.creation_time_utc).humanize()
        result_as_string = f"{result.reflection_text} ({humanized_time})"
        string += "\n" + result_as_string

    return string


def persist_reflection(raw_text):
    # Get tags
    text = str(raw_text)
    tags = {tag.strip("#") for tag in text.split() if tag.startswith("#")}

    # Get week number
    week_number = get_week_number()

    # Dump it in a table
    reflection_id = str(uuid.uuid4())

    model = ReflectionModel(reflection_id)
    model.reflection_text = text
    model.week_number = week_number
    model.tags = tags
    model.creation_time_utc = datetime.datetime.utcnow()
    model.save()


def get_week_number():
    return datetime.date.today().isocalendar()[1]


def get_delta_from_parsed_recall(recall):
    number = recall["number"]
    timeframe_type = recall["timeframe_type"]
    if timeframe_type == "m":
        # Note: this one is an approximation
        return datetime.timedelta(days=number * 28)
    if timeframe_type == "d":
        return datetime.timedelta(days=number)
    if timeframe_type == "h":
        return datetime.timedelta(hours=number)
