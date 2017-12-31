import logging
import os
import re
import shutil
import tempfile
from datetime import datetime

import boto3
from dateutil import tz
from git import Repo

logger = logging.getLogger()
logging.basicConfig()
logger.setLevel(logging.INFO)


class RepoToBucket:
    def __init__(self, repo_url, bucket_name):
        self.repo_url = repo_url
        self.bucket_name = bucket_name
        self.temp_dir = tempfile.mkdtemp(prefix='lambda_')
        self.s3 = boto3.client('s3')

    def _get_path_to(self, *file_name):
        return os.path.join(self.temp_dir, *file_name)

    def _strip_temp_dir(self, full_path):
        tempdir_end = [m.start() for m in re.finditer(r"/", full_path)][2]
        return full_path[tempdir_end + 1:]

    def _clone_repo(self):
        repo_path = self._get_path_to('repo')
        Repo.clone_from(self.repo_url, repo_path, depth=1)
        shutil.rmtree(self._get_path_to(repo_path, '.git'), ignore_errors=True)

    def _create_timestamp(self):
        utc = datetime.utcnow()
        to_zone = tz.gettz('Australia/Sydney')
        syd = datetime.utcnow().replace(tzinfo=to_zone).astimezone(to_zone)
        with open(self._get_path_to('last-update'), 'w+') as f:
            f.write('{} (UTC)\n{} (SYD)\n'.format(utc, syd))
            f.close()

    def _copy_files_into_bucket(self):
        for subdir, dirs, files in os.walk(self.temp_dir):
            for file in [x for x in files if not x.startswith('.')]:
                full_path = os.path.join(subdir, file)
                bucket_key = self._strip_temp_dir(full_path)
                logger.info("Uploading {} as {}...".format(full_path, bucket_key))
                with open(full_path, 'rb') as f:
                    response = self.s3.put_object(
                        Key=bucket_key,
                        Body=f,
                        Bucket=self.bucket_name,
                        StorageClass='REDUCED_REDUNDANCY',
                        ContentType='text/plain'
                    )

    def copy_repo_into_bucket(self):
        self._clone_repo()
        self._create_timestamp()
        self._copy_files_into_bucket()


def handler(event, context):
    logger.info('Invoking handler')
    repo_url = os.environ.get('REPO_URL', 'https://jangroth@bitbucket.org/jangroth/test-repo.git')
    bucket_name = os.environ.get('WEBSITE_BUCKET', 'ptw-web-websitebucket-aa10mrx6putg')
    RepoToBucket(repo_url, bucket_name).copy_repo_into_bucket()
    logger.info('Finished successfully.')


if __name__ == '__main__':
    handler(None, None)
