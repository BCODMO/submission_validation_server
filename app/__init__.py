from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
import logging

from app.submission.controllers import bp as submission
from app.submission.exceptions import InvalidUsage


app = Flask(__name__)
CORS(app)

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

app.config.from_pyfile('config.py')

logging.basicConfig()
if app.config.get('ENV') == 'development':
    logging.getLogger().setLevel(logging.INFO)

app.register_blueprint(submission, url_prefix='/submission')
