import json
import random
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QLineEdit, QListWidgetItem, QMainWindow, QMessageBox
from webdav3.client import Client
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Password(QMainWindow):
    def __init__(self):
        super().__init__()
        data = {
            'webdav_hostname': "https://webdav.cloud.mail.ru", 'webdav_login': "georgpyanov07@mail.ru",
            'webdav_password': "CypB0tPdV6ruDiX9w7p7"}
        self.client = Client(data)
        uic.loadUi('untitled.ui', self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Проверка на Георгия Пьянова')
        self.pushButton.clicked.connect(self.run)

    def run(self):
        self.client.download_sync(remote_path="password.txt", local_path='password.txt')
        with open('password.txt', encoding="utf8") as csvfile:
            a = csvfile.readline()
        if self.lineEdit.text() != a:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Твой IP дрес уже у меня, я тебя найду и закопаю")
            msg.setWindowTitle("ВОН!!!!!!!")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            retval = msg.exec_()
        else:
            self.second_form = Main()
            self.second_form.show()
            self.close()


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        data = {
            'webdav_hostname': "https://webdav.cloud.mail.ru", 'webdav_login': "georgpyanov07@mail.ru",
            'webdav_password': "CypB0tPdV6ruDiX9w7p7"}
        self.client = Client(data)
        self.setWindowTitle('Кабинетик Георгия Пьянова')
        uic.loadUi('untitled2.ui', self)
        self.initUI()

    def initUI(self):
        self.client.download_sync(remote_path="history.json", local_path='history.json')
        with open('history.json', encoding="utf8") as cat_file:
            data = json.load(cat_file)
        self.label.setText(f'Количество историй: {len(data)}')
        self.pushButton.clicked.connect(self.run)

    def run(self):
        my_files = self.client.list("check")
        if not my_files:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Молодец)))")
            msg.setWindowTitle("Гошенька, ты все проверил, можешь идти спать")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            retval = msg.exec_()
        else:
            self.check_form = Check()
            self.check_form.show()


class Check(QMainWindow):
    def __init__(self):
        super().__init__()
        data = {
            'webdav_hostname': "https://webdav.cloud.mail.ru", 'webdav_login': "georgpyanov07@mail.ru",
            'webdav_password': "CypB0tPdV6ruDiX9w7p7"}
        self.client = Client(data)
        uic.loadUi('untitled3.ui', self)
        self.setWindowTitle('Проверялкин')
        self.initUI()

    def initUI(self):
        my_files = self.client.list("check")
        self.my_file = "check/" + my_files[0]
        self.client.download_sync(remote_path=self.my_file, local_path='data0.json')
        with open('data0.json', encoding="utf8") as cat_file:
            self.data = json.load(cat_file)
        QListWidgetItem(f'Автор: {self.data["name"]}', self.listWidget)
        QListWidgetItem(f'Название: {self.data["history"]}', self.listWidget)
        QListWidgetItem(f'Описание: {self.data["apply"]}', self.listWidget)
        QListWidgetItem(f'Текст:', self.listWidget)
        for i in self.data["text"]:
            QListWidgetItem(f'{i[1]}/{i[0]}', self.listWidget)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.pushButton.clicked.connect(self.close)

    def accept(self):
        f = open("example.txt", 'w')
        for i in self.data["text"]:
            f.write(f'{i[1]}/{i[0]}')
        f.close()
        a = list('0123456789')
        random.shuffle(a)
        a = ''.join(a) + '.txt'
        self.client.upload_sync(remote_path=a,
                                local_path='example.txt')
        self.client.download_sync(remote_path="history.json", local_path='history.json')
        with open('history.json', encoding="utf8") as cat_file:
            data = json.load(cat_file)
        data[self.data["name"]] = {"file_name": a, "anons": self.data["apply"], 'athtor': self.data["name"]}
        with open('history.json', 'w') as cat_file:
            json.dump(data, cat_file)
        self.client.upload_sync(remote_path="history.json", local_path='history.json')
        self.client.clean(self.my_file)
        server = smtplib.SMTP_SSL(self.data["email"], 25)
        server.login('georgpyanov07@mail.ru', 'CypB0tPdV6ruDiX9w7p7')
        msg = MIMEMultipart()
        msg['From'] = 'georgpyanov07@mail.ru'
        msg['To'] = self.data["email"]
        msg['Subject'] = 'Sry_bog_bot'
        body = f'Добрый день! Уважаемый(ая) {self.data["name"]}, благодарим вас за историю, которая успешно прошла ' \
               f'модерацию и будет опубликована в ближайшее время.' \
               f'Очень ждем ваши работы еще! С уважением, команда Sry_bog_bot ' \
               f'Примечание: {self.lineEdit.text()}'
        msg.attach(MIMEText(body, 'plain'))
        server.send_message(msg)
        server.quit()
        self.close()

    def reject(self):
        self.client.clean(self.my_file)
        server = smtplib.SMTP_SSL(self.data["email"], 25)
        server.login('georgpyanov07@mail.ru', 'CypB0tPdV6ruDiX9w7p7')
        msg = MIMEMultipart()
        msg['From'] = 'georgpyanov07@mail.ru'
        msg['To'] = self.data["email"]
        msg['Subject'] = 'Sry_bog_bot'
        body = f"Добрый день! Уважаемый(ая) {self.data['name']},благодарим вас за историю, которая, к сожалению, не прошла" \
               f"модерацию." \
               f"Но это не повод расстраиваться, мы очень ждем ваши работы еще! С уважением, команда Sry_bog_bot " \
               f"Примечание: {self.lineEdit.text()}"
        msg.attach(MIMEText(body, 'plain'))
        server.send_message(msg)
        server.quit()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wa = Password()
    wa.show()
    sys.exit(app.exec())
