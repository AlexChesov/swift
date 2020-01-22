# -*- coding: utf-8 -*-
import os
import glob
import re
import sys
import smtplib
from email.mime.text import MIMEText
from email.header import Header


#smtpObj = smtplib.SMTP('10.80.96.73', 25)
# Отправитель
login = 'somr-swift@sovcombank.ru'
# Группы получателей
recipients_busines = ['fxs@sovcombank.ru', 'fc-swift2@sovcombank.ru', 'korr-schet-ValutaSWIFT@sovcombank.ru']
recipients_admins = ['golovochesovaa@sovcombank.ru']

os.chdir('/Users/alexchesov/Documents/project/swift/files')
for mt_file in glob.glob('*.prt'):
    print(mt_file)
    with open (mt_file) as mt_data0:
        for num0, line0 in enumerate(mt_data0):
            if 'Message NAK' in line0:
                global NumLime0
                NumLime0 = num0
                print('************MSG NAK DETECTED*************')
                with open(mt_file) as mt_data1:
                    for num1, line1 in enumerate(mt_data1):
                        if num1 > NumLime0:
                            if 'Date-Time' in line1:
                                DataTime = re.compile(r'Date-Time\s+:\s+\d\d/\d\d/\d\d\s\d\d:\d\d:\d\d(.*?)')
                                data = DataTime.search(line1)
                                data = (data.group())
                                print(str(data))
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
                                print('BIC = ' + bic)
                                print('Message type = ' + msg)
                                print('Reference = ' + ref)
                                msg = MIMEText('Необходимо обработать следующее сообщение:\n' + data + '\nBIC = ' + bic + '\nMessage type = ' + msg + '\nReference = ' + ref + '\n\nДля этого в Swift Alliance Access необходимо зайти в Monitoring, слева пункт Queues, поставить галочку Number of Messages > 0 и нажать Submit. \nНажать очередь LocalSwiftNaks и на закладке Monitoring нажать кнопку Show Message Instances. \nДалее обработать ВСЕ сообщения на которые были получены отрицательные подтверждения.', 'plain', 'utf-8')
                                msg['Subject'] = Header('ТЕСТ!!! MESSAGE NAK DETECTED !!!ТЕСТ', 'utf-8')
                                msg['From'] = login
                                msg['To'] = ", ".join(recipients_admins)
                                print(msg['To'])
                                global NumLime1
                                NumLime1 = num1
                                print('Выход на строке = ' + str(NumLime1) + '\nфайл = ' + mt_file + '\n\n')
                                #smtpObj = smtplib.SMTP('10.80.96.73', 25)
                                #try:
                                    #smtpObj.sendmail(msg['From'], msg['To'], msg.as_string())
                                #finally:
                                    #smtpObj.quit()
