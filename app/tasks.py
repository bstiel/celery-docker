import os
import newspaper
import hashlib

from io import BytesIO
from urllib.parse import urlparse
from celery.utils.log import get_task_logger
from minio import Minio
from minio.error import BucketAlreadyExists, BucketAlreadyOwnedByYou, NoSuchKey
from worker import app


logger = get_task_logger(__name__)


@app.task(bind=True, name='refresh')
def refresh(self, urls):
    for url in urls:
        fetch_source.s(url).delay()


@app.task(bind=True, name='fetch_source')
def fetch_source(self, url):
    logger.info(f'Build articles: {url}')
    source = newspaper.build(url)
    for article in source.articles:
        fetch_article.s(article.url).delay()


@app.task(bind=True, name='fetch_article')
def fetch_article(self, url):
    logger.info(f'Download {url}')
    article = newspaper.Article(url)
    article.download()
    logger.info(f'Parse {url}')
    article.parse()

    url = urlparse(article.source_url)
    save_article.s(url.netloc, article.title, article.text).delay()


@app.task(bind=True, name='save_article', queue='minio')
def save_article(self, bucket, key, text):

    minio_client = Minio(os.environ['MINIO_HOST'], 
        access_key=os.environ['MINIO_ACCESS_KEY'],
        secret_key=os.environ['MINIO_SECRET_KEY'],
        secure=False)

    try:
        minio_client.make_bucket(bucket, location="us-east-1")
    except BucketAlreadyExists:
        pass
    except BucketAlreadyOwnedByYou:
        pass

    hexdigest = hashlib.md5(text.encode()).hexdigest()
    try:
        st = minio_client.stat_object(bucket, key)
        update = st.etag != hexdigest
    except NoSuchKey as err:
        update = True

    if update:
        logger.info(f'Write {bucket}/{key} to minio')
        stream = BytesIO(text.encode())
        minio_client.put_object(bucket, key, stream, stream.getbuffer().nbytes)

  
    
    

