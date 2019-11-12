from pynamodb.attributes import (
    NumberAttribute,
    UnicodeAttribute,
    UnicodeSetAttribute,
    UTCDateTimeAttribute,
)

import os

from pynamodb.models import Model

REFLECTION_TABLE_NAME = os.environ.get("APP_TABLE_NAME", "")


class ReflectionModel(Model):
    class Meta:
        table_name = REFLECTION_TABLE_NAME
        region = "us-west-1"

    reflection_text = UnicodeAttribute(attr_name="ReflectionText")
    reflection_id = UnicodeAttribute(hash_key=True, attr_name="ReflectionId")
    week_number = NumberAttribute(attr_name="WeekNumber")
    tags = UnicodeSetAttribute(attr_name="Tags")
    creation_time_utc = UTCDateTimeAttribute(attr_name="CreationTimeUtc")
