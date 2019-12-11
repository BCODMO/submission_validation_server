# submission-validation 
A server that runs goodtables validations on submissions

# To run

The following environment variables are required:
```
MINIO_ENDPOINT=
MINIO_ACCESS_KEY=
MINIO_SECRET_KEY=
CELERY_BROKER_URL=
CELERY_RESULT_BACKEND=
PORT=
ENVIRONMENT=
# required if docker
GITHUB_OAUTH_TOKEN
```

To run a redis instance, run the following comands:
```
docker run -d -p 6379:6379 redis
```

To run celery
```
celery -A app.celery worker
```

To run a local version of minio, run the following commands

```
docker pull minio/minio
docker run -p 9000:9000 -e "MINIO_ACCESS_KEY=ACCESS_KEY_HERE" -e "MINIO_SECRET_KEY=SECRET_KEY_HERE" minio/minio server /data
```

and set the environment variables accordingly

