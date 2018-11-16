import os
from celery import Celery


app = Celery(include=('tasks',))
app.conf.beat_schedule = {
    'refresh': {
        'task': 'refresh',
        'schedule': float(os.environ['NEWSPAPER_SCHEDULE']),
        'args': (os.environ['NEWSPAPER_URLS'].split(','),)
    },
}