from app.minio import get_client, get_object_metadata, list_objects

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
            'name': obj_name,
            'description': obj.metadata.get(f'{CUSTOM_METADATA_PREFIX}Description', ''),
            'file_type': obj.metadata.get(f'{CUSTOM_METADATA_PREFIX}File_type', ''),
        })

    return submission_files
