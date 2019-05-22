from datetime import datetime
from worker import app


@app.task(bind=True, name='get_time')
def get_time(self):
    return datetime.now().isoformat()