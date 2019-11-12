import datetime
import uuid
from urllib.parse import parse_qs

import arrow
from chalice import Chalice
from chalicelib.reflection_model import ReflectionModel

app = Chalice(app_name="jeeves")

enabled_user_ids = ["UL7S0PCQH"]


@app.route("/")
def index():
    # Simple uptime check :grin:
    return {"hello": "world"}


@app.route(
    "/reflect", methods=["POST"], content_types=["application/x-www-form-urlencoded"]
)
def reflect():
    parsed = parse_qs(app.current_request.raw_body.decode())

    user_id = parsed.get("user_id")[0]

    if user_id not in enabled_user_ids:
        return "Hey! You're not Mitchell! Quit it 😅"

    stuff = parsed.get("text")

    reflect = stuff[0]

    if ReflectionModel.exists():
        persist_reflection(reflect)

    return f"You reflected: {reflect}"


@app.route(
    "/recall", methods=["POST"], content_types=["application/x-www-form-urlencoded"]
)
def recall():
    parsed = parse_qs(app.current_request.raw_body.decode())

    user_id = parsed.get("user_id")[0]

    if user_id not in enabled_user_ids:
        return "Hey! You're not Mitchell! Quit it 😅"

    a_week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)

    results = ReflectionModel.scan(
        filter_condition=ReflectionModel.creation_time_utc > a_week_ago
    )

    sort_fn = lambda x: x.creation_time_utc

    results = sorted(list(results), key=sort_fn, reverse=True)

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
