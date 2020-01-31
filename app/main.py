from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from celery import Celery
import logging
import json
from .constants import BCODMO_METADATA_KEY

from app.exceptions import InvalidUsage
from app.validate import validate_resource
from app.schema import infer_schema



app = Flask(__name__)
CORS(app)

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

def make_celery(app):
    celery = Celery(app.import_name, broker=app.config.get('CELERY_BROKER_URL'))
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask

    return celery

app.config.from_pyfile('config.py')

celery = make_celery(app)

# acks_late and reject_on_worker_lost ensure that the process is placed
# back onto the queue if it ends prematurely via a server restart
@celery.task(bind=True, acks_late=True, reject_on_worker_lost=True)
def validate_resource_task(self, resource):
    validation_result_url = app.config.get('SUBMISSION_VALIDATION_RESULT_URL')
    validate_resource(resource, validation_result_url)

@app.route('/schema', methods=['POST'])
def schema():
    if request.method == 'POST':
        args = request.json
        print('ARGS', args)
        submission_title = args.get('submission_title', None)
        filename = args.get('filename', None)
        options = args.get('options', {})
        try:
            # Get the submission files and a datapackage created with those files + other metadata
            resources = infer_schema(submission_title, filename, options)
            res = { 'resources': resources, 'validating': True }
            return json.dumps(res)
        except Exception as e:
            raise InvalidUsage(
                f'Error while inferring the schema of a submission: {str(e)}'
            )
        return None
@app.route('/validate', methods=['POST'])
def validate():
    if request.method == 'POST':
        resource = request.json
        if 'status' in resource[BCODMO_METADATA_KEY] and resource[BCODMO_METADATA_KEY]['status'] == 'validating':
            raise InvalidUsage('This resource is already being validated')
        try:
            validate_resource_task.delay(resource)
            res = { 'accepted': True }
            return json.dumps(res)
        except Exception as e:
            raise e
            raise InvalidUsage(
                f'Error when starting to validate a submission: {str(e)}'
            )
        return None


logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

