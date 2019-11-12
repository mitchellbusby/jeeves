from urllib.parse import urlparse, parse_qs
from chalice import Chalice
import datetime
import boto3
import os
import uuid
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute

app = Chalice(app_name='jeeves')

reflection_table_name= os.environ.get('APP_TABLE_NAME', '')

class ReflectionModel(Model):
  class Meta:
    table_name = reflection_table_name
  reflection_text = UnicodeAttribute()
  reflection_id = UnicodeAttribute(hash_key=True)

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

  persist_reflection(reflect)

  return f"You reflected: {reflect}"


def persist_reflection(raw_text):
  # Get tags
  text = str(raw_text)
  tags = text.split('#')

  # Get week number
  week_number = datetime.date.today().isocalendar()[1]

  # Dump it in a table
  db = get_db()

  attrs = {
    'week_number': week_number,
    'text': text,
    'tags': tags,
  }

  reflection_id = str(uuid.uuid4())

  model = ReflectionModel(reflection_id)
  model.reflection_text = text

  model.save()

  # db.new_item(hash_key=reflection_id, attrs=attrs).save()
