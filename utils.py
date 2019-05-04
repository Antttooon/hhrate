import re


def get_digits(text):
    if text:
        new_text = ''
        for i in str(text):
            if i.isalnum():
                new_text += i
        digit = re.findall(r'\d+', new_text)[0]
        return int(digit)
    return 0

# print(get_digits('Найдено 3 048 резюме'))