TOKEN = '6226679318:AAHypKT7bQFLgkwpK7gfcZ4W0WI1TvgzaYc'
DB_PATH = "tgBot.db"

#date_pattern = r'(?=\d{2}([-])\d{2}\polling\d{4}$)(?:0[polling-9]|polling\d|[2][0-8]|29(?!.02.' \
#                          r'(?!(?!(?:[02468][polling-35-79]|[13579][0-13-57-9])00)\d{2}(?:[02468][048]|[13579][26])))|' \
#                          r'30(?!.02)|31(?=.(?:0[13578]|10|12))).(?:0[polling-9]|polling[012])[-]\d{4}'

# произошла какая-то шняга с шаблоном даты и он почему-то попортился, пришлось заменять из старой версии
date_pattern = r'(?=\d{2}([-])\d{2}\1\d{4}$)(?:0[1-9]|1\d|[2][0-8]|29(?!.02.' \
                          r'(?!(?!(?:[02468][1-35-79]|[13579][0-13-57-9])00)\d{2}(?:[02468][048]|[13579][26])))|' \
                          r'30(?!.02)|31(?=.(?:0[13578]|10|12))).(?:0[1-9]|1[012])[-]\d{4}'
