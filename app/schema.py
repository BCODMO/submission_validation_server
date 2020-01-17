from tableschema import Table
from tabulator.loaders.aws import AWSLoader
import re
import openpyxl
import os
import boto3
from tempfile import TemporaryFile
import shutil

from .constants import BUCKET, FILES_PREFIX, BCODMO_METADATA_KEY

def clean_resource_name(name):
    name = name.casefold()
    name = re.sub(r"\s+", '_', name)
    name = re.sub(r"[^-a-z0-9._/]", '', name)
    return name

def infer_schema(submission_title, filename, options):
    print('options', options)
    # TODO if xlsx/xls, infer a schema for each sheet
    object_key = f'{submission_title}/{FILES_PREFIX}/{filename}'
    object_name = f's3://{BUCKET}/{object_key}'
    lat_col = options.pop('latitudeCol', None)
    lon_col = options.pop('longiudeCol', None)

    if (filename.endswith('.xls') or filename.endswith('.xlsx')):
        if 'sheet' in options:
            resources = [{
                'object_name': object_name,
                'options': options,
                'resource_name': clean_resource_name(options['sheet']),
            }]
        else:
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
            'options': options,
            'resource_name': clean_resource_name(filename),
        }]

    res = []
    for resource in resources:
        print('Resourc eoptions', resource['options'])
        options = resource['options']
        table = Table(resource['object_name'], **options)
        table.infer()
        schema = table.schema.descriptor
        schema[BCODMO_METADATA_KEY] = {}
        for field in schema['fields']:
            field[BCODMO_METADATA_KEY] = {}

        # Add the options to the resource schema so they can be persisted later
        if 'headers' in options:
            schema[BCODMO_METADATA_KEY]['headers'] = options['headers']
        if lat_col:
            for field in schema['fields']:
                if field['name'] == lat_col:
                    # Better name here?
                    field[BCODMO_METADATA_KEY]['definition'] = 'latitude'
        print('SCHEMA', schema)
        resObj = {
            'resource_name': resource['resource_name'],
            'schema': schema,
            'error': None,
        }
        if 'sheet' in options:
            resObj['sheet'] = options['sheet']
        res.append(resObj)
    return res


