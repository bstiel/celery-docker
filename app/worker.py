from celery import Celery


app = Celery(include=('tasks',))
app.conf.update(
    worker_pool_restarts=True
)