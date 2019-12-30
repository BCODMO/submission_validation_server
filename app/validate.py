from goodtables import validate
from .constants import BCODMO_METADATA_KEY, BUCKET

def validate_resource(resource):
    print(f'Starting the validation of a resource')
    object_key = resource[BCODMO_METADATA_KEY]['objectKey']
    object_name = f's3://{BUCKET}/{object_key}'
    report = validate(object_name, infer_schema=True)
    print('FInsihed report', report)
    # Get sheet here and pass in
    import time
    time.sleep(10)
    print('BOOM!')
