from tableschema import Table
from .minio import BUCKET, FILES_PREFIX

def infer_schema(submission_title, filename, headers=1, skip_rows=['#']):
    # TODO if xlsx/xls, infer a schema for each sheet
    table = Table(f's3://{BUCKET}/{submission_title}/{FILES_PREFIX}/{filename}')
    table.infer()
    print("INFERERED", table.schema.descriptor)
    return table.schema.descriptor
