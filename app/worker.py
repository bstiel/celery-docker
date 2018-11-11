from celery import Celery


app = Celery(include=('tasks',))
app.conf.beat_schedule = {
    'refresh': {
        'task': 'refresh',
        'schedule': 900.0,
        'args': (['http://www.faz.com'],)
    },
}