from flask import Flask, jsonify, request
from celery import Celery

app = Flask(__name__)


@app.route('/workers', methods=['GET'])
def workers():
    i = Celery().control.inspect()
    pong = i.ping()  # ping all workers
    data = [] if pong is None else list(pong.keys())
    return jsonify(data)


@app.route('/workers/<string:worker>', methods=['GET', 'DELETE'])
def worker(worker):
    control = Celery().control

    if request.method == 'GET':
        inspect = control.inspect()
        data = inspect.stats()[worker]
        return jsonify(data)

    # DELETE => shutdown worker
    control.shutdown(destination=[worker], reply=True)
    return '', 204


@app.route('/workers/<string:worker>/pool', methods=['GET', 'POST', 'DELETE'])
def pool(worker):
    control = Celery().control

    if request.method == 'GET':
        inspect = control.inspect()
        data = inspect.stats()[worker]['pool']
        return jsonify(data)

    if request.method == 'POST':
        inspect = control.inspect()
        current_concurrency = inspect.stats()[worker]['pool']['max-concurrency']
        new_concurrency = request.json['max-concurrency']
        if new_concurrency < 1:
            raise ValueError('cannot shrink concurrency pool below 1')
        elif new_concurrency > current_concurrency:
            control.pool_grow(n=new_concurrency-current_concurrency, destination=[worker])
        elif new_concurrency < current_concurrency:
            control.pool_grow(n=current_concurrency-new_concurrency, destination=[worker])
        return '', 201

    # DELETE => restart pool
    control.pool_restart(reload=True, destination=[worker])
    return '', 204


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)