from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from celery import Celery
import logging
import json

from app.exceptions import InvalidUsage
from app.validate import validate_submission_file
from app.submission import get_submission_files



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
def validate_submission_file_task(self, submission_file):
    validate_submission_file(submission_file)

@app.route('/submission/', methods=['', 'POST'])
def submission():
    if request.method == 'POST':
        body = request.json
        submission_title = body.get('submission_title', None)
        try:
            submission_files = get_submission_files(submission_title)
            for submission_file in submission_files:
                validate_submission_file_task.delay(submission_file)
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

