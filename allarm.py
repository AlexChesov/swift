# -*- coding: utf-8 -*-
import os
import glob
import subprocess
import re
import sys
import smtplib
from email.mime.text import MIMEText
from email.header import Header


#smtpObj = smtplib.SMTP('10.80.96.73', 25)
# Отправитель
login = 'swift-somr@sovcombank.ru'
# Группы получателей для боевой рассылки
recipients_busines = ['fxs@sovcombank.ru', 'fc-swift2@sovcombank.ru', 'korr-schet-ValutaSWIFT@sovcombank.ru', 'fc-ossofs@sovcombank.ru', 'KisliakovVA@msk.sovcombank.ru', 'BorinVU@sovcombank.ru']
recipients_busines_lt = ['fc-position@sovcombank.ru', 'ZakharovaEA@sovcombank.ru ', 'fxs@sovcombank.ru', 'fc-swift2@sovcombank.ru', 'korr-schet-ValutaSWIFT@sovcombank.ru', 'fc-ossofs@sovcombank.ru', 'KisliakovVA@msk.sovcombank.ru', 'BorinVU@sovcombank.ru']
recipients_admins = ['KisliakovVA@msk.sovcombank.ru', 'BorinVU@sovcombank.ru', 'fc-ossofs@sovcombank.ru']
# Для локального тестирования
#recipients_busines = ['golovochesovaa@sovcombank.ru']
#recipients_admins = ['golovochesovaa@sovcombank.ru']

os.chdir('//usr//alliance//skb//routing//warning//')
#os.chdir('//Users//alexchesov//Documents//project//swift//files')
#os.chdir('C:\\py\\swift\\files')
for mt_file in glob.glob('*.prt'):
    global delfile
    delfile =  0
    #print(mt_file)
    with open (mt_file) as mt_data0:
        for num0, line0 in enumerate(mt_data0):
            # Ищем отрицательные подтверждения NAK
            if 'Message NAK' in line0:
                delfile += 1
                #print('Удалитель файла = ' + str(delfile))
                #print('************MSG NAK DETECTED*************')
                with open(mt_file) as mt_data1:
                    for num1, line1 in enumerate(mt_data1):
                        if 'Date-Time' in line1:
                            DataTime = re.compile(r'Date-Time\s+:\s+\d\d/\d\d/\d\d\s\d\d:\d\d:\d\d(.*?)')
                            data = DataTime.search(line1)
                            data = (data.group())
                            #print(str(data))
                        if 'UMID' in line1:
                            BicNum = re.compile(r'(?<=I)[A-Z0-9]{11}(?=\d{3})')
#                            BicNum = re.compile(r'UMID\s+[A-Z0-9]{12}')
                            MsgType = re.compile(r'UMID\s+[A-Z0-9]{12}\d{3}')
                            RefNum = re.compile(r'UMID.+?(?=,)')
                            bic = BicNum.search(line1)
                            bic = (bic.group())
#                            bic = (bic.group()[6:])
                            msg = MsgType.search(line1)
                            msg = (msg.group()[-3:])
                            ref = RefNum.search(line1)
                            ref = (ref.group()[20:])
                            #print('BIC = ' + bic)
                            #print('Message type = ' + msg)
                            #print('Reference = ' + ref)
                            msg = MIMEText('Необходимо обработать следующее сообщение:\n' + data + '\nBIC = ' + bic + '\nMessage type = ' + msg + '\nReference = ' + ref + '\n\nДля этого в Swift Alliance Access необходимо зайти в Monitoring, слева пункт Queues, поставить галочку Number of Messages > 0 и нажать Submit. \nНажать очередь LocalSwiftNaks и на закладке Monitoring нажать кнопку Show Message Instances. \nДалее по перечисленным референсам найти и обработать сообщения, на которые были получены отрицательные подтверждения.', 'plain', 'utf-8')
                            msg['Subject'] = Header('MESSAGE NAK DETECTED', 'utf-8')
                            msg['From'] = login
                            msg['To'] = ", ".join(recipients_busines)
                            smtpObj = smtplib.SMTP('10.80.96.73', 25)
                            try:
                                smtpObj.sendmail(msg['From'], recipients_busines, msg.as_string())
                            finally:
                                smtpObj.quit()
            # Ищем переполнение очереди
            if 'Queue overflow' in line0:
                delfile += 1
                #print('*********Queue Overflow DETECTED*********')
                with open(mt_file) as mt_data1:
                    for num1, line1 in enumerate(mt_data1):
                        if 'Date-Time' in line1:
                            DataTime = re.compile(r'Date-Time\s+:\s+\d\d/\d\d/\d\d\s\d\d:\d\d:\d\d(.*?)')
                            data = DataTime.search(line1)
                            data = (data.group())
                            #print(str(data))
                        if 'is in overflow' in line1:
                            QueueType = re.compile(r'(?<=queue\s)[A-Za-z0-9]+(?=\sis\sin\soverflow)')
                            queue_name = QueueType.search(line1)
                            queue_name = (queue_name.group())
                            #print('Переполненная очередь - ' + queue_name)
                            msg = MIMEText('Внимание!!!\n' + data + '\n' + 'Переполнена очередь - ' + queue_name + '\nНеобходимо обработать ВСЕ сообщения в ней!', 'plain', 'utf-8')
                            msg['Subject'] = Header('QUEUE OVERFLOW', 'utf-8')
                            msg['From'] = login
                            msg['To'] = ", ".join(recipients_busines)
                            smtpObj = smtplib.SMTP('10.80.96.73', 25)
                            try:
                                smtpObj.sendmail(msg['From'], recipients_busines, msg.as_string())
                            finally:
                                smtpObj.quit()
            # Ищем подключение логического терминала
            if 'Name       : Select ACK received' in line0:
                delfile += 1
                #print('*********Select ACK received*********')
                with open(mt_file) as mt_data2:
                    for num2, line2 in enumerate(mt_data2):
                        if 'Date-Time' in line2:
                            DataTime = re.compile(r'Date-Time\s+:\s+\d\d/\d\d/\d\d\s\d\d:\d\d:\d\d(.*?)')
                            data = DataTime.search(line2)
                            data = (data.group())
                            #print('Дата: ' + str(data))
                        if 'Select ACK received:' in line2:
                            LT_Type = re.compile(r'LT\s[A-Z0-9]{9}')
                            lt_name = LT_Type.search(line2)
                            #print(str(lt_name))
                            lt_name = (lt_name.group())
                            #print('Логический терминал - ' + str(lt_name) + ' - успешно подключен!')
                            msg = MIMEText('Для информации!\n' + data + '\n' + 'Логический терминал - ' + lt_name + ' - успешно подключен! \nНикаких действий не требуется. \n\nLT SOMRRUMMA - боевой логический терминал. \nLT SOMRRUM0A - тестовый логический терминал.', 'plain', 'utf-8')
                            msg['Subject'] = Header(lt_name + ' - Select ACK received', 'utf-8')
                            msg['From'] = login
                            msg['To'] = ", ".join(recipients_busines_lt)
                            smtpObj = smtplib.SMTP('10.80.96.73', 25)
                            try:
                                smtpObj.sendmail(msg['From'], recipients_busines_lt, msg.as_string())
                            finally:
                                smtpObj.quit()
            # Ищем отключенный Message Partner
            if 'Disable Message Partner' in line0:
                delfile += 1
                #print('*********Message Partner Disable**********')
                with open(mt_file) as mt_data3:
                    for num3, line3 in enumerate(mt_data3):
                        if 'Date-Time' in line3:
                            DataTime = re.compile(r'Date-Time\s+:\s+\d\d/\d\d/\d\d\s\d\d:\d\d:\d\d(.*?)')
                            data = DataTime.search(line3)
                            data = (data.group())
                        if 'Message Partner ' in line3:
                            #print('MP Disable Detected')
                            MP_Type = re.compile(r'(?<=Partner\s)[A-Za-z0-9]+')
                            MP_Name = MP_Type.search(line3)
                            MP_Name = (MP_Name.group())
                            #print(str(MP_Name))
                            msg = MIMEText('Внимание!\n' + data + '\nMessage Partner - ' + MP_Name + ' - деактивирован!' + '\n\nСписок Message Partners:\nSOMRfromABSall - обработка исходящих сообщений, кроме 3-й категории. \nSOMRfromABS3xx - обработка исходящих сообщений 3-я категория. \nSOMRtoABS129 - обработака входящих сообщений 1, 2, 9 категорий. \nSOMRtoABS3xx - обработка входящих сообщений 3-й категории. \nSOMRPrint3xx - выгрузка печатных форм 3-й категории. \nSOMRPrint - выгрузка печатных форм, кроме 3-й категории.', 'plain', 'utf-8')
                            msg['Subject'] = Header('Message Partner - ' + MP_Name + ' - Disabled!!!', 'utf-8')
                            msg['From'] = login
                            msg['To'] = ", ".join(recipients_admins)
                            smtpObj = smtplib.SMTP('10.80.96.73', 25)
                            try:
                                smtpObj.sendmail(msg['From'], recipients_admins, msg.as_string())
                            finally:
                                smtpObj.quit()
    if delfile > 0:
        os.unlink(mt_file)
# Запускаем локальный скрипт отправки необработанных сообщений
subprocess.call("//usr//alliance//script//mail_alarm.sh")
#subprocess.call("//Users//alexchesov//Documents//project//swift//hello.sh")
#subprocess.call("C:\\project\\py\\hello.bat")
