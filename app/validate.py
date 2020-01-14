from goodtables import validate
import requests
from .constants import BCODMO_METADATA_KEY, BUCKET

def validate_resource(resource, validation_result_url):
    print(f'Starting the validation of a resource')
    object_key = resource[BCODMO_METADATA_KEY]['objectKey']
    object_name = f's3://{BUCKET}/{object_key}'
    report = validate(object_name, infer_schema=True)
    '''
    if 'tables' in report:
        for table in report['tables']:
            if 'errors' in table:
                for error in table['errors']:
                    print('error', error)
                    if 'column-number' not in error:
                        error['column-number'] = None
                    if 'row-number' not in error:
                        error['row-number'] = None
                    if 'row' not in error or error['row'] is None:
                        error['row'] = None
                print('errors after', table['errors'])
            table['source'] = resource['name']
    '''
    # Get sheet here and pass in
    import time
    #time.sleep(10)
    status = 'validate-success'
    if not report['valid']:
        status = 'validate-error'
    data = {
        'submissionTitle': resource[BCODMO_METADATA_KEY]['submissionTitle'],
        'resourceName': resource['name'],
        'status': status,
        'report': report,
    }
    r = requests.post(
        url = validation_result_url,
        json = data,
    )
    print(r.status_code, r.ok)
    print('BOOM!')
