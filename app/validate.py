from goodtables import validate
import requests
from .constants import BCODMO_METADATA_KEY, BUCKET
from .checks import latitude, longitude

def validate_resource(resource, validation_result_url):
    print(f'Starting the validation of a resource')
    object_key = resource[BCODMO_METADATA_KEY]['objectKey']
    object_name = f's3://{BUCKET}/{object_key}'
    options = {}
    checks = ['structure', 'schema']
    schema = None
    if 'schema' in resource:
        schema = resource['schema']
        if 'headers' in resource['schema'][BCODMO_METADATA_KEY]:
            options['headers'] = resource['schema'][BCODMO_METADATA_KEY]['headers']
        for field in resource['schema']['fields']:
            definition = field[BCODMO_METADATA_KEY].get('definition', None)
            if definition == 'latitude':
                checks.append({
                    'latitude-bounds': {
                        'constraint': field["name"],
                    },
                })
            if definition == 'longitude':
                checks.append({
                    'longitude-bounds': {
                        'constraint': field["name"],
                    },
                })
    try:
        if not schema:
            report = validate(object_name, infer_schema=True, checks=checks, **options)
        else:
            report = validate(object_name, schema=schema, checks=checks, **options)
        status = 'validate-success'
        if not report['valid']:
            status = 'validate-error'
    except Exception as e:
        status= 'validate-error'
        report = {
            'valid': False,
            'tables': [],
            'error': str(e),
        }

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

    data = {
        'submissionTitle': resource[BCODMO_METADATA_KEY]['submissionTitle'],
        'resourceName': resource['name'],
        'status': status,
        'report': report,
    }
    print("Posting to ", validation_result_url)
    r = requests.post(
        url = validation_result_url,
        json = data,
    )
    print(r.status_code, r.ok)
    print('BOOM!')
