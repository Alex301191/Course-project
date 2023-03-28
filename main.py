import requests
import json
import time
from tqdm import tqdm


class YaUploader:
    def __init__(self, token):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    def create_new_folder(self, folder_name):
        url = "https://cloud-api.yandex.net/v1/disk/resources"
        headers = self.get_headers()
        params = {"path": folder_name}
        response = requests.put(url, headers=headers, params=params)
        return response.json()

    def create_new_folder_in_folder(self, folder_name, album_name):
        url = "https://cloud-api.yandex.net/v1/disk/resources"
        headers = self.get_headers()
        params = {"path": f"{folder_name}/{album_name}"}
        response = requests.put(url, headers=headers, params=params)
        return response.json()

    def get_upload_link(self, disk_file_path, album_name, url, filename):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = self.get_headers()
        params = {"path": f"{disk_file_path}/{album_name}/{filename}",
                  "overwrite": "true",
                  "url": url}
        response = requests.post(upload_url, headers=headers, params=params)
        return response.json()

    def upload_file_to_disk(self, folder_name, album_name, url, name, size):
        i = 0
        print(f"Количество фото для загрузки: {len(name)}")
        self.create_new_folder(folder_name)
        self.create_new_folder_in_folder(folder_name, album_name)
        print("Директории для сохранения данных успешно созданы")
        answer = []
        for i in tqdm(range(len(name)), desc="Photo upload progress"):
            photo_data = {}
            href = self.get_upload_link(disk_file_path=folder_name, album_name=album_name,
                                        url=url[i], filename=name[i]).get("href", "")
            requests.post(href, files={"file": name[i]})
            time.sleep(0.5)
            photo_data["file_name"] = name[i]
            photo_data["size"] = size[i]
            answer.append(photo_data)
        print(json.dumps(answer, sort_keys=True, ensure_ascii=True, indent=4))


class VK:
    def __init__(self, token, user_id):
        self.token = token
        self.id = user_id

    def get_photo_data(self, album_name):
        url = "https://api.vk.com/method/photos.get"
        api = requests.get(url=url, params={
            'owner_id': VK_user_id,
            'access_token': VK_token,
            'photo_sizes': 0,
            'v': 5.131,
            'extended': 1,
            'album_id': album_name
        })
        return json.loads(api.text)

    def get_photo_url(self, js):
        data = js
        count_photo = data["response"]["count"]
        i = 0
        count = 50
        photos_url_list = []
        with tqdm(total=count_photo, desc="Get photos urls progress") as pbar:
            while i <= count_photo:
                for files in data["response"]["items"]:
                    file_url = files["sizes"][-1]["url"]
                    photos_url_list.append(file_url)
                    time.sleep(0.001)
                    pbar.update(1)
                i += count
        return photos_url_list

    def get_photo_size(self, js):
        data = js
        count_photo = data["response"]["count"]
        i = 0
        count = 50
        photos_sizes = []
        with tqdm(total=count_photo, desc="Get photos sizes progress") as pbar:
            while i <= count_photo:
                for files in data["response"]["items"]:
                    file_size = files["sizes"][-1]["type"]
                    photos_sizes.append(file_size)
                    time.sleep(0.001)
                    pbar.update(1)
                i += count
        return photos_sizes

    def get_photo_name(self, js):
        data = js
        count_photo = data["response"]["count"]
        i = 0
        count = 50
        photos_name_list = []
        file_format = '.png'
        with tqdm(total=count_photo, desc="Get photos names progress") as pbar:
            while i <= count_photo:
                for files in data["response"]["items"]:
                    nam = str(files["likes"]['count'])
                    filename = ''.join([nam, file_format])
                    photos_name_list.append(filename)
                    time.sleep(0.001)
                    pbar.update(1)
                i += count
        return photos_name_list


if __name__ == '__main__':
    Yandex_token = ""
    VK_token = ''
    VK_user_id = ''
    print("Введите наименование источника загрузки фото (profile, wall, saved): \n")
    album_name = str(input())
    folder_name = 'My_photos_from_VK'
    downloader = VK(token=VK_token, user_id=VK_user_id)
    js = downloader.get_photo_data(album_name)
    url = downloader.get_photo_url(js)
    name = downloader.get_photo_name(js)
    size = downloader.get_photo_size(js)
    uploader = YaUploader(token=Yandex_token)
    uploader.upload_file_to_disk(folder_name, album_name, url, name, size)
    print("Файлы успешно загружены")
