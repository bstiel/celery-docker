# celery-docker

## using `docker-compose`

### Up
`$ docker-compose up -d`

### Scale
`$ docker-compose up -d --scale worker=2`
`$ docker-compose up -d --scale worker=1`

### Down
`$ docker-compose down`

## using `docker-stack`

### Up
`$ docker stack deploy -c docker-stack.yml celery-docker-example`

### Scale
`$ docker service scale celery-docker-example_worker=2`
`$ docker service scale celery-docker-example_worker=1`

### Down
`$ docker stack rm celery-docker-example`
