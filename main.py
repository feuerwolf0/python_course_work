from mytokens import TOKEN_VK, TOKEN_YA
import requests
import os.path, os
from tqdm import tqdm
import shutil
import json
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

class VK:
    def __init__(self, access_token, user_id, v='5.131'):
        self.token = access_token
        self.user_id = user_id
        self.v = v
        self.BASE_URL = 'https://api.vk.com/method/'
        self.user_info = self.get_user_info()
        self.owner_id = self.user_info['response'][0]['id']
        self.first_name = self.user_info['response'][0]['first_name']
        self.last_name = self.user_info['response'][0]['last_name']

    def get_user_info(self):
        print('Получаю информацию о пользователе с id: {}'.format(self.user_id))
        method = 'users.get'
        params = {
            'user_ids': self.user_id,
            'access_token': self.token,
            'v': self.v
        }
        response = requests.get(self.BASE_URL+method,params)
        return response.json()

    #Функция возвращает список всех изображений
    def get_user_pics(self):
        print('Получаю все фотографии профиля {} {}'.format(self.first_name, self.last_name))
        method = 'photos.get'
        params = {
            'access_token': self.token,
            'v': self.v,
            'owner_id' : self.owner_id,
            'album_id': 'profile',
            'rev': 1,
            'extended': 1,
            'count': 1000,
            'photo_sizes': 1
        }
        response = requests.get(self.BASE_URL+method, params)
        print('У пользователя {} {} {} фото'.format(self.first_name, self.last_name, response.json()['response']['count']))
        return response.json()['response']['items']
    
    # Функция возвращает список id всех альбомы пользователя
    def get_all_ids_albums(self):
        print('Получаю список всех альбомов {} {}'.format(self.first_name, self.last_name))
        method = 'photos.getAlbums'
        params = {
            'access_token': self.token,
            'v': self.v,
            'owner_id' : self.owner_id,
            'photo_sizes': 1
        }
        r = requests.get(url=self.BASE_URL+method, params=params)
        if not 'error' in r.json():
            print(f"Найдено {r.json()['response']['count']} альбомов")
        else:
            print('Ошибка. Возможно у пользователя нет альбомов или они закрыты')
            return []
        return [item['id'] for item in r.json()['response']['items']]
    
    # Функция возвращает список всех изображений из всех альбомов
    def get_all_pics_from_albums(self):
        albums = self.get_all_ids_albums()
        if not albums:
            return []
        method = 'photos.get'
        params = {
            'access_token': self.token,
            'v': self.v,
            'owner_id' : self.owner_id,
            'album_id': '{}'.format(*albums),
            'rev': 1,
            'extended': 1,
            'count': 1000,
            'photo_sizes': 1
        }
        r = requests.get(url=self.BASE_URL+method, params=params)
        print(f"Найдено {r.json()['response']['count']} фото в альбомах")
        return r.json()['response']['items']
    

    # Функция загружает все изображения в папку files
    def download_all_pics(self, path,list_pics, nums=5):
        headers = {
           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
           'accept-encoding': 'gzip, deflate, br',
           'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
        }
        # Цикл по всем изображениям
        json_pics = []
        for pic in tqdm(list_pics[:nums], ncols=80, ascii=True, desc='Загрузка изображений'):
            # Название изображения (кол-во лайков)
            pic_name = pic['likes']['count']
            # url изображения
            pic_url = pic['sizes'][-1]['url']
            # Если папки images нет - создаю ее
            if not os.path.isdir(path):
                os.mkdir(path)
            # Создаю флаг
            flag = 0
            # Если файл с таким именем уже есть - добавляю дату в название файла
            if os.path.isfile(f'{path}/{pic_name}.png'):
                with open(f'{path}/{pic_name}_{pic["date"]}.png', 'wb') as f_pic:
                    r = requests.get(pic_url,headers)
                    f_pic.write(r.content)
                flag = 1
            else:
                with open(f'{path}/{pic_name}.png', 'wb') as f_pic:
                    r = requests.get(pic_url,headers)
                    f_pic.write(r.content)
            # Создаю json файл
            pic_info = {}
            # Если файлу дописывалась дата в UNIX - дописываю ее название файла в json
            if flag:
                 pic_info = {"file_name": f"{pic_name}_{pic['date']}.png",\
            "size": f"{pic['sizes'][-1]['height']}x{pic['sizes'][-1]['width']}"}
            else: 
                pic_info = {"file_name": f"{pic_name}.png",\
                "size": f"{pic['sizes'][-1]['height']}x{pic['sizes'][-1]['width']}"}
            json_pics.append(pic_info)
        # Сохраняю info.json
        with open('info.json', 'at') as f:
            json.dump(json_pics,f, indent=3, ensure_ascii=True)

class YaUploader:
    def __init__(self,token,foldername):
        self.token = token
        self.headers = {
            'Authorization': 'OAuth {}'.format(self.token)
        }
        self.BASE_URL = 'https://cloud-api.yandex.net/'
        self.foldername = foldername

    # Функция создает папку на яндекс диске
    def folder_create(self):
        method = 'v1/disk/resources'
        params = {
            'path': self.foldername
        }
        r = requests.put(url=self.BASE_URL+method, headers=self.headers, params=params)
        if r.status_code == 201:
            print(f'Папка {self.foldername} на я.диск успешно создана')
            return f'OK {r.status_code}'
        elif r.status_code == 409:
            print(f'Папка {self.foldername} уже есть на я.диске')
            return f'OK {r.status_code}'
        else:
            print(f'Ошибка создания папки: {r.status_code}')
            return f'ERROR {r.status_code}'
        

    def upload(self,path):
        # Создаю папку на диске
        self.folder_create()
        # Получаю все файлы в папке
        files = [file for file in os.listdir(path) if os.path.isfile(f'{path}/{file}')]
        for file in tqdm(files, ascii=True, desc='Загружено на YaDisk'):
            with open(f'{path}/{file}', 'rb') as my_file:
                r = requests.put(url=self.get_link_upload(file),headers=self.headers,files={'file':my_file})
                # Если файл не загрузится - печатаю и возвращаю ошибку
                if (r.status_code != 200) and (r.status_code != 201):
                    print('\nОшибка загрузки файла: {}'.format(r.status_code))
                    return f'Ошибка {r.status_code}'
        print(f'Файлы в количестве {len(files)} успешно загружены в папку {self.foldername}')

    # Функция получает ссылку для загрузки изображения
    def get_link_upload(self, filename):
        method = 'v1/disk/resources/upload'
        params = {
            'path': f'{self.foldername}/{filename}',
            'overwrite': True
        }
        r = requests.get(url=self.BASE_URL+method, headers=self.headers, params=params)
        return r.json()['href']


class GoogleUploader:
    def __init__(self,foldername):
        self.gauth = GoogleAuth()
        self.gauth.LocalWebserverAuth()
        self.drive = GoogleDrive(self.gauth)
        self.foldername = foldername
        # Получаю словарь вида filename: id
        self.file_dict = self.get_file_list()
    
    # Функция создает папку в google drive
    def create_folder(self):
        if not self.foldername in self.file_dict:
            file_metadata = {
                'title': self.foldername,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = self.drive.CreateFile(file_metadata)
            folder.Upload()
        else:
            print('Папка {} уже создана на gDrive'.format(self.foldername))

    # Функция возвращает словарь вида filename: id файлов на Google Drive (нужна для исключения дублирования папок)
    def get_file_list(self):
        file_list = self.drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
        file_dict = {}
        for file1 in file_list:
            file_dict[file1['title']] = file1['id']
        return file_dict
    
    # Функция загружает изображения на Google Drive
    def upload(self,path):
        # Создаю папку на Google Drive
        self.create_folder()
        # Получаю словарь файлов в папке, куда будут загружаться фото
        file_list = self.drive.ListFile({'q': "'{}' in parents and trashed=false".format(self.file_dict[self.foldername])}).GetList()
        titles = []
        # создаю список файлов лежащих в папке куда будут загружаться фото
        [titles.append(file['title']) for file in file_list]
        print('Начинаю загружать файлы на Google Drive')
        # Загружаю все фото из локальной папки на Google Drive
        for filename in tqdm(os.listdir(path), ncols=80, ascii=True, desc='Загрузка изображений'):
            # Если файл уже есть в папке на gdrive - пропускаю его
            if not filename in titles:
                my_file = self.drive.CreateFile({'title': f'{filename}','parents': [{'id': self.file_dict[self.foldername]}]})
                my_file.SetContentFile(os.path.join(path,filename))
                my_file.Upload()
            else:
                print(f'Файл {filename} уже есть на Google Drive')
        print('Файлы успешно загружены на Google Drive')


def main():
    # Удаляю старый info.json
    if os.path.isfile('info.json'):
        os.remove('info.json')
    # получаю токены из файла mytokens.py
    token_vk = TOKEN_VK
    token_ya = TOKEN_YA
    # Id страницы пользователя
    user_id = 'snbrnbeast'
    # Название для локальной папки с фотографиями
    path_to_pics = 'images'
    # Количество изображений для скачивания
    num_pics = 10
    # Количетсво изображений для скачивания из альбомов
    num_pics_from_album = 5
    # создаю объект класса vk
    vk = VK(token_vk, user_id)
    # Скачиваю все изображения профиля
    vk.download_all_pics(path_to_pics,vk.get_user_pics(),num_pics)
    # Скачиваю все изображения из альбомов
    vk.download_all_pics(path_to_pics,vk.get_all_pics_from_albums(),num_pics_from_album)
    # создаю объект класса YaUploader
    ya = YaUploader(token_ya,user_id)
    # загружаю все изображения на яндекс диск
    ya.upload(path_to_pics)

    # Для работы необходим файл client_secrets.json созданный на https://console.cloud.google.com/apis/dashboard
    # для библиотеки pydrive https://pythonhosted.org/PyDrive/quickstart.html
    # создаю объект класса GoogleUploader
    gd = GoogleUploader(user_id)
    # Загружаю все файлы из локальной папки на Google Drive
    gd.upload(path_to_pics)
    # Удаляю локальную папку images
    shutil.rmtree(path_to_pics)
    print(f'Локальная папка {path_to_pics} удалена со всеми вложенными файлами')

if __name__ == '__main__':
    main()
