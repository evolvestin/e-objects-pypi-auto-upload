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
temp_folder = 'temp'


if os.environ.get('server') is None:
    os.environ['version'] = '1.0.0'


def delete(action, name, exc):
    os.chmod(name, stat.S_IWRITE)
    os.remove(name)


while True:
    sleep(10)
    Repo.clone_from('https://github.com/steve10live/e-objects', temp_folder)  # клонируем библиотеку с гитхаба
    current_version_text = re.sub('\n', '', os.environ.get('version'))
    current_version = int(re.sub(r'\D', '', current_version_text))
    try:
        get_new_version = open(temp_folder + '/version')
        new_version_text = re.sub('\n', '', get_new_version.read())
        new_version = int(re.sub(r'\D', '', new_version_text))
        get_new_version.close()
    except IndexError and Exception:
        new_version_text = '0.0.0'
        new_version = 0
    print('new version =', new_version_text, '| current version =', current_version_text)
    if new_version > current_version:
        os.makedirs('egg')  # создаем папку для egg-info мусора
        shutil.rmtree(temp_folder + '/.git', onerror=delete)  # удаляем папку .git (она нам не нужна)
        shutil.copytree(temp_folder, '.', dirs_exist_ok=True)  # копируем содержимое библиотеки прямо в папку скрипта
        temp_files = os.listdir(temp_folder)  # сохраняем список файлов библиотеки в переменную
        shutil.rmtree(temp_folder, onerror=delete)  # удаляем папку с файлами библиотеки
        os.system("python setup.py sdist egg_info --egg-base egg/")  # упаковываем библиотеку
        shutil.rmtree('egg', onerror=delete)  # удаляем egg-info мусор вместе с папкой после упаковки

        for file in temp_files:  # очищаем главную папку от остатков библиотеки
            try:
                os.remove(file)
            except IndexError and Exception:
                shutil.rmtree(file, onerror=delete)

        os.system(command % data)  # закачиваем упакованную библиотеку на pypi.org
        shutil.rmtree('dist', onerror=delete)  # удаляем папку с упакованной библиотекой

        if os.environ.get('api'):
            connection = heroku3.from_key(os.environ.get('api'))
            for app in connection.apps():
                config = app.config()
                config['version'] = new_version_text
    else:
        shutil.rmtree(temp_folder, onerror=delete)  # удаляем папку с файлами библиотеки
