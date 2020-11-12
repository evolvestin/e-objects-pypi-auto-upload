import os
import re
import stat
import shutil
import heroku3
import objects
from time import sleep
from objects import bold, code
from git.repo.base import Repo
command = 'twine upload --repository-url https://upload.pypi.org/legacy/ dist/* --username evolvestin --password '
temp_folder = 'temp'

if os.environ.get('version') is None:
    os.environ['version'] = '1.0.0'


def delete(action, name, exc):
    action.clear(), exc.clear()
    os.chmod(name, stat.S_IWRITE)
    os.remove(name)


while True:
    sleep(10)
    Repo.clone_from('https://github.com/evolvestin/e-objects', temp_folder)  # клонируем библиотеку с гитхаба
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

        os.system(command + os.environ['PASSWORD'])  # закачиваем упакованную библиотеку на pypi.org
        shutil.rmtree('dist', onerror=delete)  # удаляем папку с упакованной библиотекой

        if os.environ.get('api'):
            connection = heroku3.from_key(os.environ.get('api'))
            for app in connection.apps():
                config = app.config()
                config['version'] = new_version_text

        release_notify_text = bold('Released:\n') + code('e-objects ') + 'ver. ' + code(new_version_text)
        objects.AuthCentre(os.environ['TOKEN']).send_dev_message(release_notify_text, tag=None)
        # коннектимся к Bot API телеграма через e-objects и тут же отправляем в мой чатик с уведомлениями от ботов
    else:
        shutil.rmtree(temp_folder, onerror=delete)  # удаляем папку с файлами библиотеки
