from flask import Blueprint, request, session
import io
import json
import os
import logging
from minio import Minio
from minio.error import (
    ResponseError, BucketAlreadyOwnedByYou, BucketAlreadyExists
)
import traceback

from .exceptions import InvalidUsage

# production does not save to s3 currently
OFFLINE = os.environ.get('ENVIRONMENT') == 'production'


bp = Blueprint('submission', __name__, url_prefix='/submission')

@bp.route('/', methods=['POST'])
def start_submission_validation():
    if request.method == 'POST':
        body = request.json
        submission_title = body.get('submission_title', None)
        print('Starting validaton submission title', submission_title)
        try:
            res = { 'accepted': True }
            return json.dumps(res)
        except Exception as e:
            raise InvalidUsage(
                f'Error when starting to validate a submission: {str(e)}'
            )
    return None

def get_minio_object(bucket, object_name):
    minio_client = get_minio_client()
    res = minio_client.get_object(bucket, object_name)
    file_content = res.read().decode()
    pass

def get_minio_client():
    host = os.environ['MINIO_ENDPOINT']
    access_key = os.environ['MINIO_ACCESS_KEY']
    secret_key = os.environ['MINIO_SECRET_KEY']
    if not host or not access_key or not secret_key:
        raise Exception ('Minio host, access_key and secret_key required')

    return Minio(
        host,
        access_key=access_key,
        secret_key=secret_key,
        secure=False,
    )
