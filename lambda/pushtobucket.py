import boto3
import os
import logging
from datetime import datetime
from dateutil import tz

logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_name = 'last-update'

def add_tmp_path(file_name):
    return os.path.join('/tmp', file_name)

def create_timestamp_file(file_name):
    utc = datetime.utcnow()
    to_zone = tz.gettz('Australia/Sydney')
    syd = datetime.utcnow().replace(tzinfo=to_zone).astimezone(to_zone)
    with open(add_tmp_path(file_name),'w+') as f:
        f.write('{} (UTC)\n{} (SYD)\n'.format(utc, syd))
        f.close()

def copy_file_to_bucket(file_name, bucket_name):
    s3 = boto3.client('s3')
    with open(add_tmp_path(file_name),'rb') as f:
        response = s3.put_object(
            Key=file_name,
            Body=f,
            Bucket=bucket_name,
            StorageClass='REDUCED_REDUNDANCY',
            ContentType='text/plain'
        )
        print(response)
        f.close()

def handler(event, context):
    logger.info('Invoking handler')
    bucket_name = os.environ.get('WEBSITE_BUCKET', 'local')
    create_timestamp_file(file_name)
    copy_file_to_bucket(file_name, bucket_name)
    logger.info('Finished successfully.')

if __name__ == '__main__':
    handler(None, None)
