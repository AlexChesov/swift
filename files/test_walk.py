import os

for filenames in os.listdir('C:\\project\\swift\\files'):
    if filenames.endswith('.prt'):
        print('Файлы в каталоге ' + filenames)
        