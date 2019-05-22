from datetime import datetime
from worker import app


print(f'Loading {__name__}')


@app.task(bind=True, name='get_time')
def get_time(self):
    return datetime.now().isoformat()
