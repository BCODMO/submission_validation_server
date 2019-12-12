import ntpath
import json
import re
from flask import current_app as app
from io import BytesIO
from datapackage import Package

from app.minio import BUCKET, get_client, get_object_metadata, list_objects

FILE_PREFIX = 'files'
CUSTOM_METADATA_PREFIX = 'X-Amz-Meta-'

def get_submission_files(submission_title):
    mc = get_client()
    obj_prefix = f'{submission_title}/{FILE_PREFIX}/'
    objects = list_objects(mc, obj_prefix)
    print('objects after', objects)
    submission_files = []
    for obj_name in objects:
        obj = get_object_metadata(mc, obj_name)
        submission_files.append({
            'object_name': obj_name,
            'description': obj.metadata.get(f'{CUSTOM_METADATA_PREFIX}Description', ''),
            'file_name': ntpath.basename(obj_name),
            'file_type': obj.metadata.get(f'{CUSTOM_METADATA_PREFIX}File_type', ''),
        })

    # TODO get metadata from metadata file
    metadata = None
    dp = create_datapackage(submission_title, submission_files, metadata)

    return submission_files, dp

def clean_resource_name(name):
    name = name.casefold()
    name = re.sub(r"\s+", '_', name)
    name = re.sub(r"[^-a-z0-9._/]", '', name)
    return name

def create_datapackage(submission_title, submission_files, metadata):
    minio_url = app.config.get('MINIO_ENDPOINT')
    package = Package({ 'name': submission_title })
    for submission in submission_files:
        package.add_resource({
            'name': clean_resource_name(submission['file_name']),
            'path': f'http://{minio_url}/minio/{BUCKET}/{submission["object_name"]}',

        })
    # TODO decide if we validate here?
    '''
    try:
        validate(package.descriptor)
    except Exception as e:
        raise e
    '''

    return package.descriptor

def add_datapackage(dp):
    pass
