import boto3
import datetime
import random
import os

file_name = 'test.txt'

def add_tmp_path(file_name):
    return os.path.join('/tmp', file_name)

def create_random_file(file_name):
    content = random.randint(1, 1000) 
    with open(add_tmp_path(file_name),'w+') as f:
        f.write('{} - {}\n'.format(datetime.datetime.now(), content))
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
    bucket_name = event['WebsiteBucket']
    create_random_file(file_name)
    copy_file_to_bucket(file_name, bucket_name)

if __name__ == '__main__':
    handler(None, None)
