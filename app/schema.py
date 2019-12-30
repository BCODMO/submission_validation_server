from tableschema import Table
from tabulator.loaders.aws import AWSLoader
import re
import openpyxl
import os
import boto3
from tempfile import TemporaryFile
import shutil

from .constants import BUCKET, FILES_PREFIX

def clean_resource_name(name):
    name = name.casefold()
    name = re.sub(r"\s+", '_', name)
    name = re.sub(r"[^-a-z0-9._/]", '', name)
    return name

def infer_schema(submission_title, filename):
    # TODO if xlsx/xls, infer a schema for each sheet
    object_key = f'{submission_title}/{FILES_PREFIX}/{filename}'
    object_name = f's3://{BUCKET}/{object_key}'
    if filename.endswith('.xls') or filename.endswith('.xlsx'):
        loader = AWSLoader()
        b = loader.load(object_name, mode='b')

        # Create copy for remote source
        # For remote stream we need local copy (will be deleted on close by Python)
        new_bytes = TemporaryFile()
        shutil.copyfileobj(b, new_bytes)
        b.close()
        b = new_bytes
        b.seek(0)
        wb = openpyxl.load_workbook(b)
        # TODO decide if this is too slow for larger excel sheets

        resources = []
        for sheet_name in wb.sheetnames:
            print('Sheet name', sheet_name)
            resources.append({
                'object_name': object_name,
                'options': { 'sheet': sheet_name },
                'resource_name': clean_resource_name(sheet_name),

            })

    else:
        resources = [{
            'object_name': object_name,
            'options': {},
            'resource_name': clean_resource_name(filename),
        }]

    res = []
    for resource in resources:
        table = Table(resource['object_name'], options=resource['options'])
        table.infer()
        resObj = {
            'resource_name': resource['resource_name'],
            'schema': table.schema.descriptor,
            'error': None,
        }
        if 'sheet' in resource['options']:
            resObj['sheet'] = resource['options']['sheet']
        res.append(resObj)
    return res


