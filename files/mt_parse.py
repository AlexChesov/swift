import os
import re
import sys
import smtplib
from email.mime.text import MIMEText
from email.header    import Header


smtpObj = smtplib.SMTP('10.80.96.73', 25)
# Отправитель
login = 'somr-swift@sovcombank.ru'
# Группы получателей
recipients_busines = ['fxs@sovcombank.ru', 'fc-swift2@sovcombank.ru', 'korr-schet-ValutaSWIFT@sovcombank.ru']
recipients_admins = ['golovochesovaa@sovcombank.ru']

with open ('mt_test1.prt') as mt_data:
    for num0, line0 in enumerate(mt_data):
        line0 = mt_data
        if 'Message NAK' in line0:
            print ('************MSG NAK DETECTED*************')
            with open ('mt_test1.prt') as mt_data:
                for num1, line in enumerate(mt_data):
                    if 'Date-Time' in line:
                        DataTime = re.compile(r'Date-Time\s+:\s+\d\d/\d\d/\d\d\s\d\d:\d\d:\d\d(.*?)')
                        data = DataTime.search(line)
                        data = (data.group())
                        print(str(data))
                    if 'UMID' in line:
                        BicNum = re.compile(r'UMID\s+[A-Z0-9]{12}')
                        MsgType = re.compile(r'UMID\s+[A-Z0-9]{12}\d{3}')
                        RefNum = re.compile(r'UMID.+?(?=,)')
                        bic = BicNum.search(line)
                        msg = MsgType.search(line)
                        ref = RefNum.search(line)
                        bic = (bic.group()[6:])
                        print ('BIC = ' + bic)
                        msg = (msg.group()[-3:])
                        print ('Message type = ' + msg)
                        ref = (ref.group()[20:])
                        print ('Reference = ' + ref)
                        # Проверяем наличие сообщения о переполнении очереди LocalSwiftNaks
                        msg = MIMEText('Необходимо обработать следующее сообщение:\n' + data + '\nBIC = ' + bic + '\nMessage type = ' + msg + '\nReference = ' + ref + '\n\nДля этого в Swift Alliance Access необходимо зайти в Monitoring, слева пункт Queues, поставить галочку Number of Messages > 0 и нажать Submit. \nНажать очередь LocalSwiftNaks и на закладке Monitoring нажать кнопку Show Message Instances. \nДалее обработать ВСЕ сообщения на которые были получены отрицательные подтверждения.', 'plain', 'utf-8')
                        msg['Subject'] = Header('ТЕСТ! Получен ТЕСТ!!!', 'utf-8')
                        msg['From'] = login
                        msg['To'] = ", ".join(recipients_admins)
                #break
        for num2, line in enumerate(mt_data):
            if num2 > 12:
                if 'overflow' in line:
                    print('*********Overflow DETECTED**********')
                if 'Time' in line:
                    DataTime = re.compile(r'Date-Time\s+:\s+\d\d/\d\d/\d\d\s\d\d:\d\d:\d\d(.*?)')
                    data = DataTime.search(line)
                    data = (data.group())
                    print(str(data))
#try:
#    smtpObj.sendmail(msg['From'], recipients_admins, msg.as_string())
#finally:
#    smtpObj.quit()