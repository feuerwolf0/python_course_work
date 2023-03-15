### Курсовая работа Python:  
Токены загружаются из файла mytokens.py  
**Основные настройки:**  
*user_id* - id пользователя вконтакте с которым работать  
*path_to_pics* - название локальной папки изображений, куда будут загружаться изображения. Удаляется после завершения работы приложения.  
*num_pic* - количество изображений для бэкапа.  

**Дополнительные задания:**
Добавил функции получения всех изображений из альбомов.  
Для скачивания изображений используется универсальная функция *download_all_pics(path,list_pics, nums)*,
где:  
*path* - название локальной папки для сохранения изображений  
*list_pics* - список изображений для скачивания (можно получить используя функцию *get_user_pics()* или *get_all_pics_from_albums()*)  
*nums* -  количество изображений для бэкапа  
**Основные настройки:**  
*num_pics_from_album* - количество изображений из альбомов для бэкапа