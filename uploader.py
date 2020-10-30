import os
import re
import stat
import base64
import shutil
import heroku3
from time import sleep
from ast import literal_eval
from git.repo.base import Repo
command = 'twine upload --repository-url %(url)s --username %(username)s --password %(password)s'
data = 'eyd1c2VybmFtZSc6ICdldm9sdmVzdGluJywgJ3VybCc6ICdodHRwczovL3VwbG9hZC5weXBpLm9yZy9sZWdhY3kv' \
       'IGRpc3QvKicsICdwYXNzd29yZCc6ICdZd2V5VHU3aFlyVHZNRGZqN0FuWDJmWUxHNlp6R2VSZXd5eW04UWFZJ30='
data = literal_eval(base64.b64decode(data).decode('utf-8'))
if os.environ.get('server') is None:
    os.environ['version'] = '1.0.0'


def delete(action, name, exc):
    os.chmod(name, stat.S_IWRITE)
    os.remove(name)


while True:
    sleep(10)
    Repo.clone_from('https://github.com/steve10live/e-objects', 'objects/')
    current_version_text = re.sub(r'\D', '', os.environ.get('version'))
    current_version = int(current_version_text)
    try:
        get_new_version = open('objects/version')
        new_version_text = re.sub(r'\D', '', get_new_version.read())
        new_version = int(new_version_text)
        get_new_version.close()
    except IndexError and Exception:
        new_version_text = '0.0.0'
        new_version = 0
    print('new version =', new_version_text, '| current version =', current_version_text)
    if new_version > current_version:
        os.system('python setup.py sdist')
        os.system(command % data)
        if os.environ.get('api'):
            connection = heroku3.from_key(os.environ.get('api'))
            for app in connection.apps():
                config = app.config()
                config['version'] = new_version_text
    shutil.rmtree('objects/', onerror=delete)
