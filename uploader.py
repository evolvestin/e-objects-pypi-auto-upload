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
data = 'eyd1c2VybmFtZSc6ICdldm9sdmVzdGluJywgJ3VybCc6ICdodHRwczovL3VwbG9hZC5weXBpLm9yZy9sZWdhY3kvIGRpc3' \
       'Qvb2JqZWN0cy8qJywgJ3Bhc3N3b3JkJzogJ1l3ZXlUdTdoWXJUdk1EZmo3QW5YMmZZTEc2WnpHZVJld3l5bThRYVknfQ=='
print(data)
data = literal_eval(base64.b64decode(data).decode('utf-8'))
if os.environ.get('server') is None:
    os.environ['version'] = '1.0.0'


def delete(action, name, exc):
    os.chmod(name, stat.S_IWRITE)
    os.remove(name)


while True:
    sleep(10)
    Repo.clone_from('https://github.com/steve10live/e-objects', 'objects/')
    current_version_text = os.environ.get('version')
    current_version = int(re.sub(r'\D', '', current_version_text))
    try:
        get_new_version = open('objects/version')
        new_version_text = get_new_version.read()
        new_version = int(re.sub(r'\D', '', new_version_text))
        get_new_version.close()
    except IndexError and Exception:
        new_version_text = '0.0.0'
        new_version = 0
    print('new version =', new_version_text, '| current version =', current_version_text)
    if new_version > current_version:
        os.system('python objects/setup.py sdist')
        os.system(command % data)
        if os.environ.get('api'):
            connection = heroku3.from_key(os.environ.get('api'))
            for app in connection.apps():
                config = app.config()
                config['version'] = new_version_text
    shutil.rmtree('objects/', onerror=delete)
