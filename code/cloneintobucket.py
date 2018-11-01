import boto3
import logging
import os
import re
import shutil
import subprocess
import tempfile
from datetime import datetime
from dateutil import tz

# from jinja2 import Environment, FileSystemLoader

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


class GitHelper:
    GIT_BINARY_TAR = 'git-2.4.3.tar'

    def __init__(self, project_base_dir):
        self.project_base_dir = project_base_dir
        self.git_dir = os.path.join(self.project_base_dir, 'git-binaries')

    def install(self):
        logger.info('Installing git into {}'.format(self.git_dir))
        os.mkdir(self.git_dir)
        # untar into git_dir
        subprocess.check_output(['tar', '-C', self.git_dir, '-xf', self.GIT_BINARY_TAR])
        os.environ['GIT_EXEC_PATH'] = os.path.join(self.git_dir, 'usr/libexec/git-core')
        os.environ['GIT_TEMPLATE_DIR'] = os.path.join(self.git_dir, 'usr/share/git-core/templates')
        os.environ['LD_LIBRARY_PATH'] = os.path.join(self.git_dir, 'usr/lib64')

    def run_command(self, command):
        return subprocess.check_output([os.path.join(os.environ['GIT_EXEC_PATH'], 'git'), command],
                                       universal_newlines=True)


class RepoToBucket:
    def __init__(self, repo_url, bucket_name, runs_local):
        self.repo_url = repo_url
        self.bucket_name = bucket_name
        self.runs_local = runs_local
        self.temp_dir = tempfile.mkdtemp(prefix='RepoToBucket_')
        self.repo_dir = self._get_path_to('repo')
        self.s3 = boto3.client('s3')
        self.git_helper = GitHelper(self.temp_dir)
        self.git_helper.install()

    def _get_path_to(self, *file_name):
        return os.path.join(self.temp_dir, *file_name)

    def _strip_temp_dir(self, full_path):
        tempdir_end = [m.start() for m in re.finditer(r"/", full_path)][2]
        return full_path[tempdir_end + 1:]

    # def _configure_git(self):
    #     logger.info('installing git...')
    #     os.system('tar -C {} -xf git-2.4.3.tar'.format(self.temp_dir))
    #     os.environ['GIT_EXEC_PATH'] = self._get_path_to('usr/libexec/git-core')
    #     os.environ['GIT_TEMPLATE_DIR'] = self._get_path_to('usr/share/git-core/templates')

    def _clone_repo(self):
        logger.info('cloning repo...')
        repo_path = self._get_path_to('repo')
        os.system('GIT_TEMPLATE_DIR={}; {}/git clone --depth 1 {} {}'.format(
            self._get_path_to('/usr/share/git-core/templates'), self._get_path_to('usr/libexec/git-core'),
            self.repo_url, repo_path))
        shutil.rmtree(self._get_path_to(repo_path, '.git'), ignore_errors=True)

    def _create_timestamp_file(self):
        logger.info('creating timestamp file...')
        utc = datetime.utcnow()
        to_zone = tz.gettz('Australia/Sydney')
        syd = datetime.utcnow().replace(tzinfo=to_zone).astimezone(to_zone)
        with open(self._get_path_to('last-update'), 'w+') as f:
            f.write('{} (UTC)\n{} (SYD)\n'.format(utc, syd))
            f.close()

    def _copy_into_bucket(self, bucket_key, file):
        self.s3.put_object(
            Key=bucket_key,
            Body=file,
            Bucket=self.bucket_name,
            StorageClass='REDUCED_REDUNDANCY',
            ContentType='text/plain'
        )

    def _copy_files_into_bucket(self):
        for subdir, dirs, files in os.walk(self._get_path_to('repo')):
            for file in [x for x in files if not x.startswith('.')]:
                full_path = os.path.join(subdir, file)
                bucket_key = self._strip_temp_dir(full_path)
                logger.info("Uploading {} as {}...".format(full_path, bucket_key))
                with open(full_path, 'rb') as f:
                    self._copy_into_bucket(bucket_key, f)

    def copy_repo_into_bucket(self):
        self._configure_git()
        self._clone_repo()
        self._create_timestamp_file()
        self._copy_files_into_bucket()


# class BucketToWeb:
#     def __init__(self, path_to_files, path_to_web):
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
    logger.info('Lambda invoked')

    repo_url = os.environ.get('REPO_URL', 'https://jangroth@bitbucket.org/jangroth/test-repo.git')
    bucket_name = os.environ.get('WEBSITE_BUCKET', 'ptw-web-websitebucket-aa10mrx6putg')
    runs_local = event.get('local', None)

    RepoToBucket(repo_url, bucket_name, runs_local).copy_repo_into_bucket()

    logger.info('Finished successfully.')


if __name__ == '__main__':
    # handler(None, None)
    path_to_files = '/home/jan/data/dev/projects/notes/'
    path_to_web = '/home/jan/data/dev/projects/pushtoweb/www'
    # BucketToWeb(path_to_files, path_to_web).generate_web_page()
