from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from celery import Celery
import logging
import json

from app.exceptions import InvalidUsage
from submission_validation import infer_schema, validate_resource
from submission_validation.constants import BCODMO_METADATA_KEY


app = Flask(__name__)
CORS(app)


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def make_celery(app):
    celery = Celery(app.import_name, broker=app.config.get("CELERY_BROKER_URL"))
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask

    return celery


app.config.from_pyfile("config.py")

celery = make_celery(app)

# acks_late and reject_on_worker_lost ensure that the process is placed
# back onto the queue if it ends prematurely via a server restart
@celery.task(bind=True, acks_late=True, reject_on_worker_lost=True)
def validate_resource_task(self, resource):
    validate_resource(resource)


@app.route("/schema", methods=["POST"])
def schema():
    if request.method == "POST":
        args = request.json
        submission_id = args.get("submission_id", None)
        filename = args.get("filename", None)
        options = args.get("options", {})
        try:
            # Get the submission files and a datapackage created with those files + other metadata
            schemas = infer_schema(submission_id, filename, options)
            res = {
                "statusCode": 200,
                "body": {"error": False, "errorText": None, "schemas": schemas,},
            }
        except Exception as e:
            res = {
                "statusCode": 500,
                "body": {
                    "error": True,
                    "errorText": f"Error while inferring the schema of a submission: {str(e)}",
                    "schemas": None,
                },
            }

        return json.dumps(res), res.get("statusCode", 200)


@app.route("/validate", methods=["POST"])
def validate():
    if request.method == "POST":
        resource = request.json
        try:
            validate_resource_task.delay(resource)
            res = {
                "statusCode": 200,
                "body": {"accepted": True, "error": False, "errorText": None},
            }
        except Exception as e:
            res = {
                "statusCode": 500,
                "body": {
                    "accepted": False,
                    "errorText": f"Error when starting to validate a submission: {str(e)}",
                    "error": True,
                },
            }
        return json.dumps(res), 200


logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
