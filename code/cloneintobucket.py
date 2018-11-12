import logging
import os
import re
import shutil
import subprocess
import tempfile
from datetime import datetime

import boto3
from dateutil import tz

root = logging.getLogger()
if root.handlers:
    for handler in root.handlers:
        root.removeHandler(handler)
logging.basicConfig(
    format='%(asctime)s %(name)-25s %(levelname)-8s %(message)s',
    level=logging.INFO)
logger = logging.getLogger()
logging.getLogger('boto3').setLevel(logging.ERROR)
logging.getLogger('botocore').setLevel(logging.ERROR)

GIT_FOLDER = 'git-binaries'
NOTES_FOLDER = 'notes'


class GitHelper:
    GIT_BINARY_TAR = 'git-2.4.3.tar'

    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.git_dir = os.path.join(self.base_dir, '%s' % GIT_FOLDER)
        self._install()

    def _install(self):
        logger.info('Installing git into {}'.format(self.git_dir))
        os.mkdir(self.git_dir)
        subprocess.check_output(['tar', '-C', self.git_dir, '-xf', self.GIT_BINARY_TAR], stderr=subprocess.STDOUT, universal_newlines=True)
        os.environ['GIT_EXEC_PATH'] = os.path.join(self.git_dir, 'usr/libexec/git-core')
        os.environ['GIT_TEMPLATE_DIR'] = os.path.join(self.git_dir, 'usr/share/git-core/templates')
        os.environ['LD_LIBRARY_PATH'] = os.path.join(self.git_dir, 'usr/lib64')

    def run_command(self, *commands):
        git_binary = os.path.join(os.environ['GIT_EXEC_PATH'], 'git')
        output = subprocess.check_output([git_binary] + list(commands), stderr=True, universal_newlines=True)
        logger.info('run command: {} {}\n{}'.format(git_binary, commands, output))


class WebHelper:

    def __init__(self, site_dir):
        self.site_dir = site_dir

    def _create_timestamp_file(self):
        logger.info('creating timestamp file...')
        utc = datetime.utcnow()
        to_zone = tz.gettz('Australia/Sydney')
        syd = datetime.utcnow().replace(tzinfo=to_zone).astimezone(to_zone)
        with open(os.path.join(self.site_dir, 'last-update'), 'w+') as f:
            f.write('{} (UTC)\n{} (SYD)\n'.format(utc, syd))
            f.close()

    def generate_website(self):
        self._create_timestamp_file()


class RepoToBucket:
    def __init__(self, repo_url, bucket_name, local_run):
        self.repo_url = repo_url
        self.bucket_name = bucket_name
        self.local_run = local_run
        self.s3 = boto3.client('s3')
        self.base_dir = tempfile.mkdtemp()
        self.site_dir = self._get_path_to(NOTES_FOLDER)
        self.git_helper = GitHelper(self.base_dir)
        self.web_helper = WebHelper(self.site_dir)

    def _get_path_to(self, *file_names):
        return os.path.join(self.base_dir, *file_names)

    def _strip_temp_dir(self, full_path):
        tempdir_end = [m.start() for m in re.finditer(r"/", full_path)][2]
        return full_path[tempdir_end + 1:]

    def _clone_repo(self):
        logger.info('cloning repo...')
        self.git_helper.run_command('clone', '--depth', '1', '{}'.format(self.repo_url), '{}'.format(self.site_dir))
        shutil.rmtree(self._get_path_to(self.site_dir, '.git'), ignore_errors=True)

    def _copy_into_bucket(self, bucket_key, file):
        self.s3.put_object(
            Key=bucket_key,
            Body=file,
            Bucket=self.bucket_name,
            StorageClass='ONEZONE_IA',
            ContentType='text/plain'
        )

    def _generate_website(self):
        self.web_helper.generate_website()

    def _copy_site_to_bucket(self):
        for subdir, dirs, files in os.walk(self._get_path_to('repo')):
            for file in [x for x in files if not x.startswith('.')]:
                full_path = os.path.join(subdir, file)
                bucket_key = self._strip_temp_dir(full_path)
                logger.info("Uploading {} as {}...".format(full_path, bucket_key))
                with open(full_path, 'rb') as f:
                    self._copy_into_bucket(bucket_key, f)

    def create(self):
        self._clone_repo()
        self._generate_website()
        if not self.local_run:
            self._copy_site_to_bucket()


# class BucketToWeb:
#     def __init__(self, path_to_web, path_to_files):
#         self.path_to_files = path_to_files
#         self.path_to_web = path_to_web
#         self.path_to_templates = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
#         self.jinja_environment = Environment(
#             autoescape=False,
#             loader=FileSystemLoader(self.path_to_templates),
#             trim_blocks=False)
#
#     def _is_markdown_file(self, file):
#         return os.path.isfile(os.path.join(self.path_to_files, file)) and file.endswith('.md')
#
#     def _get_name(self, file):
#         return os.path.splitext(file)[0]
#
#     def _get_path_to(self, *file_name):
#         # TODO: refactor paths
#         return os.path.join(self.path_to_files, *file_name)
#
#     def _get_updates(self, file):
#         # output = subprocess.check_output(["git", "--git-dir='{}.git'".format(self.path_to_files), "log", "--pretty='%cr'", "--", "{}".format(self._get_path_to(file))])
#         output = os.system("git --git-dir='{}.git' log".format(self.path_to_files))
#         print(output)
#         return '12'
#
#     def _read_file_info(self):
#         result = []
#         files = [f for f in os.listdir(self.path_to_files) if self._is_markdown_file(f)]
#         for file in files:
#             result.append(
#                 {'name': self._get_name(file),
#                  'updated': self._get_updates(file)})
#         return result
#
#     def _render_template(self, template_name, context):
#         return self.jinja_environment.get_template(template_name).render(context)
#
#     def _generate_index_page(self, file_info):
#         with open(os.path.join(self.path_to_web, 'index.html'), 'w') as f:
#             html = self._render_template('index.html.jinja', file_info)
#             f.write(html)
#
#     def generate_web_page(self):
#         file_info = self._read_file_info()
#         self._generate_index_page({'notes': file_info})


def handler(event, context):
    logger.info('invoking lambda')

    repo_url = os.environ.get('REPO_URL', 'https://jangroth@bitbucket.org/jangroth/test-repo.git')
    bucket_name = os.environ.get('WEBSITE_BUCKET', 'test-push-to-web-site')
    local_run = event.get('local', None) is not None
    RepoToBucket(repo_url, bucket_name, local_run).create()

    logger.info('Lambda finished successfully.')


if __name__ == '__main__':
    handler({'local': True}, {})
