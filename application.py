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
            self.client.download_sync(remote_path="history.json", local_path='history.json')
            with open('history.json', encoding="utf8") as cat_file:
                data = json.load(cat_file)
            self.label.setText(f'Количество историй: {len(data)}')


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
            f.write(f'{i[1]}/{i[0]}\n')
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
        user = "georgpyanov07@mail.ru"
        passwd = "CypB0tPdV6ruDiX9w7p7"
        server = "smtp.mail.ru"
        port = 587
        subject = 'Sry_bog_bot'
        to = self.data["email"]
        charset = 'Content-Type: text/plain; charset=utf-8'
        mime = 'MIME-Version: 1.0'
        haha = False
        for i in ['полина', 'наташа', 'чулпан', 'юлия']:
            if i in self.data["name"].lower():
                haha = True
        if haha:
            text = f'Добрый день! Уважаемый(ая) {self.data["name"]}, благодарим вас за историю, которая успешно прошла ' \
                   f'модерацию и будет опубликована в ближайшее время. А ЕЩЕ У ВАС САМОЕ КРАСИВОЕ ИМЯ НА ПЛАНЕТЕ))))' \
                   f'Очень ждем ваши работы еще! С уважением, команда Sry_bog_bot ' \
                   f'Примечание: {self.lineEdit.text()}'
        else:
            text = f'Добрый день! Уважаемый(ая) {self.data["name"]}, благодарим вас за историю, которая успешно прошла ' \
                   f'модерацию и будет опубликована в ближайшее время.' \
                   f'Очень ждем ваши работы еще! С уважением, команда Sry_bog_bot ' \
                   f'Примечание: {self.lineEdit.text()}'
        body = "\r\n".join((f"From: {user}", f"To: {to}",
                            f"Subject: {subject}", mime, charset, "", text))
        try:
            smtp = smtplib.SMTP(server, port)
            smtp.starttls()
            smtp.ehlo()
            smtp.login(user, passwd)
            smtp.sendmail(user, to, body.encode('utf-8'))
        except smtplib.SMTPException as err:
            print('Что - то пошло не так...')
            raise err
        finally:
            smtp.quit()
        self.close()

    def reject(self):
        self.client.clean(self.my_file)
        user = "georgpyanov07@mail.ru"
        passwd = "CypB0tPdV6ruDiX9w7p7"
        server = "smtp.mail.ru"
        port = 587
        subject = 'Sry_bog_bot'
        to = self.data["email"]
        charset = 'Content-Type: text/plain; charset=utf-8'
        mime = 'MIME-Version: 1.0'
        text = f"Добрый день! Уважаемый(ая) {self.data['name']},благодарим вас за историю, которая, к сожалению, не прошла" \
               f"модерацию." \
               f"Но это не повод расстраиваться, мы очень ждем ваши работы еще! С уважением, команда Sry_bog_bot " \
               f"Примечание: {self.lineEdit.text()}"
        body = "\r\n".join((f"From: {user}", f"To: {to}",
                            f"Subject: {subject}", mime, charset, "", text))
        try:
            smtp = smtplib.SMTP(server, port)
            smtp.starttls()
            smtp.ehlo()
            smtp.login(user, passwd)
            smtp.sendmail(user, to, body.encode('utf-8'))
        except smtplib.SMTPException as err:
            print('Что - то пошло не так...')
            raise err
        finally:
            smtp.quit()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wa = Password()
    wa.show()
    sys.exit(app.exec())
