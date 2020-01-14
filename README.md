# submission-validation 
A server that runs goodtables validations on submissions

# To run

The following environment variables are required:
```
MINIO_ENDPOINT=(localhost:9000)
MINIO_ACCESS_KEY=(ACCESS_KEY_HERE)
MINIO_SECRET_KEY=(SECRET_KEY_HERE)
CELERY_BROKER_URL=(localhost:6379)
CELERY_RESULT_BACKEND=(localhost:6379)
PORT=(5380)
ENVIRONMENT=(development)
SUBMISSION_VALIDATION_RESULT_URL=(localhost:8080/file/validationResult)
# copies of above env variables for boto
S3_ENDPOINT=(http://localhost:9000)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
# required if docker
GITHUB_OAUTH_TOKEN
```

To run a redis instance, run the following comands:
```
docker run -d -p 6379:6379 redis
```

To run celery
```
sudo apt install python-celery-common
celery -A app.celery worker
```

To run a local version of minio, run the following commands

```
docker pull minio/minio
docker run -p 9000:9000 -e "MINIO_ACCESS_KEY=ACCESS_KEY_HERE" -e "MINIO_SECRET_KEY=SECRET_KEY_HERE" minio/minio server /data
```

and set the environment variables accordingly

