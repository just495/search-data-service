import re

import geocoder
import pandas as pd

from utils import compare


class ParserBase:
    def prepare(self, text):
        return text.replace('\n', '')

    def parse(self, text):
        raise NotImplementedError()


class ParserDate(ParserBase):
    _date_formats_regexp = [
        # 12.10.2018
        r"(\d\d.\d\d.\d\d\d\d)",
        # 12-10-2018
        r"(\d\d-\d\d-\d\d\d\d)",
        # 12/10/2018
        r"(\d\d/\d\d/\d\d\d\d)",
        # 2018-12-10
        r"(\d\d\d\d-\d\d-\d\d)",
        # 10 января 2018
        r"(\d{1,2} (?:январ|феврал|март|апрел|ма|июн|июл|сентябр|октябр|ноябр|декабр)[яйь] \d{4})",
        # 10 января
        r"(\d{1,2} (?:январ|феврал|март|апрел|ма|июн|июл|сентябр|октябр|ноябр|декабр)[яйь])",
        # января 2018
        r"(?:январ|феврал|март|апрел|ма|июн|июл|сентябр|октябр|ноябр|декабр)[яйь] \d{4}",
    ]

    def parse(self, text):
        result = []
        for regex in self._date_formats_regexp:
            matches = re.finditer(regex, text, re.MULTILINE)

            for match in matches:
                text = text.replace(match.group(0), '')
                result.append({'text': match.group(0), 'type': 'date'})
        return result


class ParserPlaceName(ParserBase):
    def parse(self, text):
        result = []
        text = self.prepare(text)
        # разбиваем текст на предложения
        sentences = re.split('[.!?]', text)
        for sentence in sentences:
            # разбиваем предложения на части
            parts = re.split('[,;:]', sentence)
            for part in parts:
                # разбиваем части предложения на слова
                words = re.split('[ ]', part)
                for key, word in enumerate(words):
                    # проспускаем слов, если+ оно не начинается с верхнего регистра
                    if not re.match('(^[А-Я]{1})', word):
                        continue
                    # пытаемся геокодировать срез части предложений
                    geocoded = self.geocode(words[key:])
                    if geocoded:
                        result.append(geocoded)

        return result

    def geocode(self, words):
        result = None
        search = None
        for index in range(len(words)):
            search = ' '.join(words[:index+1])
            g = geocoder.yandex(search, lang='ru-RU')
            if g:
                found_place = g.json['address'].split(',')[-1]
                # если результат совпадает на 67% с поиском
                if compare(found_place, search) >= 67:
                    result = g
                    break
                elif index+1 >= len(found_place.split(' ')):
                    break
            else:
                break
        if result and result.json['quality'] in ['country', 'province', 'locality', 'area']:
            return {'text': search,
                    'type': 'place',
                    'address': result.json['address']}

        return None


class ParserPersonName(ParserBase):
    
    def __init__(self):
        self._df_names = pd.read_csv('data/names.csv')  # база имен
        self._df_surnames = pd.read_csv('data/surnames.csv')  # база фамилий
    
    def parse(self, text):
        result = []
        text = self.prepare(text)
        # разбиваем текст на предложения
        sentences = re.split('[.!?]', text)
        for sentence in sentences:
            # разбиваем предложения на части
            parts = re.split('[,;:]', sentence)
            for part in parts:
                # разбиваем части предложения на слова
                words = part.split(' ')
                for key, word in enumerate(words):
                    names = []
                    while re.match('(^[А-Я]{1})', word):
                        if self.is_given_name(word):
                            names.append(word)
                            del words[key]
                            try:
                                word = words[key]
                            except IndexError:
                                break
                        else:
                            break

                    if names:
                        result.append({'text': ' '.join(names), 'type': 'name'})
        return result

    def is_given_name(self, word):
        """Определяет является ли переданная строка именем собственным"""
        patronymic_regex = r"(^[А-Я][а-я]+(?:ович|овна|евич|евна|ич|ична|инична)$)"
        if not self._df_surnames[self._df_surnames['surname'] == word].empty or \
           not self._df_names[self._df_names['name'] == word].empty or \
           re.match(patronymic_regex, word):
            return True
        return False


class ParserMoney(ParserBase):
    currencies = [{
        "short": 'USD',
        "symbol": '$'
    }, {
        "short": "EUR",
        "symbol": '€'
    }, {
        "short": "RUB",
        "symbol": '₽'
    }]

    def parse(self, text):
        result = []
        regex = r'\d+[ ]{0,1}'
        regex += '(?:(?:[{symbols}])|(?:{shorts}))'.format(symbols='|'.join([cur['symbol'] for cur in self.currencies]),
                                                           shorts='|'.join([cur['short'] for cur in self.currencies]))
        matches = re.finditer(regex, text, re.MULTILINE)

        for match in matches:
            result.append({'text': match.group(0), 'type': 'money'})

        return result


class Parser:
    _parsers = [ParserDate, ParserMoney, ParserPlaceName, ParserPersonName]
    
    def parse(self, text):
        result = []
        for parser in self._parsers:
            result += parser().parse(text)
        return result
