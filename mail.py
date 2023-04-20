import json
from webdav3.client import Client

data = {
 'webdav_hostname': "https://webdav.cloud.mail.ru", 'webdav_login': "georgpyanov07@mail.ru",
 'webdav_password': "CypB0tPdV6ruDiX9w7p7"}
client = Client(data)


def take_history(name):
    client.download_sync(remote_path="history.json", local_path='history.json')
    with open('history.json', encoding="utf8") as cat_file:
        data = json.load(cat_file)
    f = data[name]
    with open(f['file_name'], encoding="utf8") as csvfile:
        return csvfile.readlines()


def anons_history():
    client.download_sync(remote_path="history.json", local_path='history.json')
    with open('history.json', encoding="utf8") as cat_file:
        data = json.load(cat_file)
    c = []
    for i in data.keys():
        c.append([i, data[i]['anons'], data[i]['athtor']])
    return c


client.upload_sync(remote_path="history.json", local_path="history.json")