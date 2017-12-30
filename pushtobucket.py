import boto3
import datetime
import random

def create_random_file(file_name):
    content = random.randint(1, 1000) 
    with open(file_name,'w+') as f:
        f.write('{} - {}\n'.format(datetime.datetime.now(), content))
        f.close()

def copy_file_to_bucket(file_name, bucket_name):
    s3 = boto3.client('s3')
    with open(file_name,'rb') as f:
        response = s3.put_object(
            Key=file_name, 
            Body=f, 
            Bucket=bucket_name, 
            StorageClass='REDUCED_REDUNDANCY',
            ContentType='text/plain'
        )
        print(response)
        f.close()

if __name__ == '__main__':
    file_name = 'test.txt'
    bucket_name = 'ptw-infrastructure-websitebucket-k0aguzr8adez'
    create_random_file(file_name)
    copy_file_to_bucket(file_name, bucket_name)
