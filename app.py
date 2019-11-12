from urllib.parse import urlparse, parse_qs
from chalice import Chalice
import datetime
import boto3
import os
import uuid
import json
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, UnicodeSetAttribute, UTCDateTimeAttribute
import arrow

app = Chalice(app_name='jeeves')

reflection_table_name= os.environ.get('APP_TABLE_NAME', '')

class ReflectionModel(Model):
  class Meta:
    table_name = reflection_table_name
    region = 'us-west-1'
  reflection_text = UnicodeAttribute(attr_name='ReflectionText')
  reflection_id = UnicodeAttribute(hash_key=True, attr_name='ReflectionId')
  week_number = NumberAttribute(attr_name='WeekNumber')
  tags = UnicodeSetAttribute(attr_name='Tags')
  creation_time_utc = UTCDateTimeAttribute(attr_name="CreationTimeUtc")

enabled_user_ids = ['UL7S0PCQH']

@app.route('/')
def index():
  # Simple uptime check :grin:
  return {'hello': 'world'}

@app.route('/reflect', methods=["POST"], content_types=['application/x-www-form-urlencoded'])
def reflect():
  parsed = parse_qs(app.current_request.raw_body.decode())

  user_id = parsed.get('user_id')[0]

  if user_id not in enabled_user_ids:
    return "Hey! You're not Mitchell! Quit it 😅"

  stuff = parsed.get('text')

  reflect = stuff[0]

  if ReflectionModel.exists():
    persist_reflection(reflect)

  return f"You reflected: {reflect}"

@app.route('/recall', methods=["POST"], content_types=['application/x-www-form-urlencoded'])
def recall():
  parsed = parse_qs(app.current_request.raw_body.decode())

  user_id = parsed.get('user_id')[0]

  if user_id not in enabled_user_ids:
    return "Hey! You're not Mitchell! Quit it 😅"

  a_week_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)

  results = ReflectionModel.scan(filter_condition=ReflectionModel.creation_time_utc > a_week_ago)

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