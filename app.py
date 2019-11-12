from urllib.parse import urlparse, parse_qs
from chalice import Chalice
import datetime
import boto3
import os
import uuid
import json
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, UnicodeSetAttribute

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


enabled_user_ids = ['UL7S0PCQH']

@app.route('/')
def index():
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

  week_number_to_find = get_week_number() - 1

  results = ReflectionModel.scan(filter_condition=ReflectionModel.week_number == week_number_to_find)

  results_mapped = [result.reflection_text for result in results]

  return json.dumps(results_mapped)

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

  model.save()


def get_week_number():
  return datetime.date.today().isocalendar()[1]