#!/bin/bash
# Проверяем наличие файлов в каталоге WARNING
if A=$(find /usr/alliance/skb/routing/warning -name "*.prt" -exec echo -n "1" \; ); [ "$A" = "" ]
then echo "NO FILES" > /dev/null
else
for file in `find /usr/alliance/skb/routing/warning -type f -name "*.prt"`
do
   /usr/alliance/script/flip.linux -u $file;
   sed -i 's/[\x01\x03]//g' $file;
#   sed -i 's/ \{1,\}/ /g' $file;
   cat $file | mailx -r swift-somr@sovcombank.ru -s "SOMRRUMM ALARM" fc-ossofs@sovcombank.ru fc-swift2@sovcombank.ru fxs@sovcombank.ru korr-schet-ValutaSWIFT@sovcombank.ru KisliakovVA@msk.sovcombank.ru BorinVU@sovcombank.ru;
   rm $file;
done
fi
