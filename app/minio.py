from flask import current_app as app
from minio import Minio
from minio.error import (
    ResponseError,
    BucketAlreadyOwnedByYou,
    BucketAlreadyExists,
    NoSuchBucket,
)

from .constants import BUCKET, FILES_PREFIX

def get_object(mc, object_name):
    res = mc.get_object(BUCKET, object_name)
    file_content = res.read().decode()
    pass

def get_object_metadata(mc, object_name):
    return mc.stat_object(BUCKET, object_name)

def list_objects(mc, prefix):
    try:
        objects = mc.list_objects_v2(BUCKET, prefix)
        return [obj.object_name for obj in objects]
    except NoSuchBucket as e:
        return []
    except Exception as e:
        print(type(e))
        raise e

def get_client():
    host = app.config.get('MINIO_ENDPOINT')
    access_key = app.config.get('MINIO_ACCESS_KEY')
    secret_key = app.config.get('MINIO_SECRET_KEY')
    if not host or not access_key or not secret_key:
        raise Exception ('Minio host, access_key and secret_key required')

    return Minio(
        host,
        access_key=access_key,
        secret_key=secret_key,
        secure=False,
    )
