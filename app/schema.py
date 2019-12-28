from tableschema import Table
import re
from .minio import BUCKET, FILES_PREFIX

def clean_resource_name(name):
    name = name.casefold()
    name = re.sub(r"\s+", '_', name)
    name = re.sub(r"[^-a-z0-9._/]", '', name)
    return name

def infer_schema(submission_title, filename):
    # TODO if xlsx/xls, infer a schema for each sheet
    object_name = f's3://{BUCKET}/{submission_title}/{FILES_PREFIX}/{filename}'
    resources = [{
        'object_name': object_name,
        'options': {},
        'resource_name': clean_resource_name(filename),
    }]

    res = []
    for resource in resources:
        table = Table(resource['object_name'], options=resource['options'])
        table.infer()
        res.append({
            'resource_name': resource['resource_name'],
            'schema': table.schema.descriptor,
            'error': None,
        })
    print("res", res)
    return res


