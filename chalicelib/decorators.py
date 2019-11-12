from functools import wraps

from chalice import Chalice

from urllib.parse import parse_qs

ENABLED_USER_IDS = ["UL7S0PCQH"]


def requires_user_id(app_ref: Chalice):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            parsed = parse_qs(app_ref.current_request.raw_body.decode())

            user_id = parsed.get("user_id")[0]

            if user_id not in ENABLED_USER_IDS:
                return "Hey! You're not Mitchell! Quit it 😅"
            return f(*args, **kwargs)

        return wrapped

    return wrapper
