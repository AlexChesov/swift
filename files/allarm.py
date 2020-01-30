# coding=utf-8
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
recipients_admins = ['fc-ossofs@sovcombank.ru']

for mt_file in os.walk('C:\\project\\swift\\*.prt'):
    print(mt_file)
    with open ('mt_file') as mt_data0:
        for num0, line0 in enumerate(mt_data0):
    #        print(int(num0))
            if 'Message NAK' in line0:
                global NumLime0
                NumLime0 = num0
    #            print('Строка с NAK = ' + str(NumLime0))
                print('************MSG NAK DETECTED*************')
                with open('mt_file') as mt_data1:
                    for num1, line1 in enumerate(mt_data1):
                        if num1 > NumLime0:
    #                        print(num1)
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
                                print('Выход на строке = ' + str(NumLime1))
                                try:
                                    smtpObj.sendmail(msg['From'], msg['To'], msg.as_string())
                                finally:
                                    smtpObj.quit()
                                break
    print('\n\nВыход из первого цикла. ' + 'Последняя обработанная строка = ' + str(NumLime1) + '\n\n')

    # Если ALARM сдвоенный, то нужно проверить наличие второго, как правило это переполненная очередь
    with open('mt_test1.prt') as mt_data2:
        for num2, line2 in enumerate(mt_data2):
            if num2 > NumLime1:
                if 'Queue overflow' in line2:
                    global NumLime2
                    NumLime2 = num2
                    print('*********Queue Overflow DETECTED**********')
                    #print ('Текущая строка нумер' + str(NumLime2))
                    with open('mt_test1.prt') as mt_data3:
                        for num3, line3 in enumerate(mt_data3):
                            if num3 > NumLime2:
                                #print ('Работаем со строкой ' + str(num3))
                                if 'Date-Time' in line3:
                                    DataTime = re.compile(r'Date-Time\s+:\s+\d\d/\d\d/\d\d\s\d\d:\d\d:\d\d(.*?)')
                                    data = DataTime.search(line3)
                                    data = (data.group())
                                    print(str(data))
                                if 'is in overflow' in line3:
                                    QueueType = re.compile(r'(?<=queue\s)[A-Za-z]+(?=\sis\sin\soverflow)')
                                    queue_name = QueueType.search(line3)
                                    queue_name = (queue_name.group())
                                    print('Переполненная очередь - ' + queue_name)
                        msg = MIMEText(data + '\n' + 'Очередь ' + queue_name + ' переполнена! Необходимо обработать ВСЕ сообщения в ней!', 'plain', 'utf-8')
