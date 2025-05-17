import pandas as pd
import re
import string
import spacy
import numpy as np


class Prepare_Text:
    def __init__(self):
        self.nlp_en = spacy.load("en_core_web_sm")
        self.nlp_ru = spacy.load("ru_core_news_sm")

    def prepare_text(self, text: str) -> str:
        return self.__processing_cell__(text)

    def light_prepare_text(self, text: str) -> str:
        if type(text) == str and len(text) > 0:
            return self.__remove_extra_spaces_and_line_breaks__(text)
        else:
            return ""

    def prepare_docs(
        self, path: str, columns: list[str], processing_columns: list[str],
        num_of_docs: int
    ) -> pd.DataFrame:
        docs = pd.read_excel(path)
        docs = docs.loc[:num_of_docs, columns]
        docs = docs.fillna("")
        docs = docs.astype(str)

        return self.__processing__(docs, processing_columns)

    def light_prepare_docs(
        self, path: str, columns: list[str], num_of_docs: int
    ) -> pd.DataFrame:
        docs = pd.read_excel(path)
        docs = docs.loc[:num_of_docs, columns]
        docs = docs.fillna("")
        docs = docs.astype(str)

        for row in range(num_of_docs):
            for column in docs.columns:
                if type(docs.loc[row, column]
                       ) == str and len(docs.loc[row, column]) > 0:
                    docs.loc[
                        row,
                        column] = self.__remove_extra_spaces_and_line_breaks__(
                            docs.loc[row, column]
                        )
                else:
                    docs.loc[row, column] = ""

        return docs

    def __first_is_en__(self, cell: str) -> bool:
        '''
        Определяет начинается строка с символа русского алфавита или
        английского алфавита.\n
        cell: строка.\n
        Возвращает true, если строка начинается с символа английского алфавита.
        '''

        index_first_en = re.search(r"[a-zA-Z]", cell)
        index_first_ru = re.search(r"[а-яА-Я]", cell)

        return True if index_first_en and (
            not (index_first_ru) or
            index_first_ru and index_first_en.start() < index_first_ru.start()
        ) else False

    def __split_into_en_and_ru__(self, cell: str) -> list[(bool, str)]:
        '''
        Разделяет строку на части, в которых содержатся символы принадлежащие
        только русскому или английскому алфавиту (то есть в строке с русскими
        символами не будет символов английского языка и наоборот, остальные символы
        не удаляются).\т
        cell: строка.\n
        Возврщает массив кортежей
        (True(если начинается с символа английского алфавита), подстрока).
        '''

        parts = []
        is_en = self.__first_is_en__(cell)
        part = ""
        for symb in cell:
            if is_en == (symb in string.ascii_letters) or not (symb.isalpha()):
                part += symb
            else:
                parts.append((is_en, part))
                part = symb
                is_en = not (is_en)

        if part:
            parts.append((is_en, part))

        return parts

    def __remove_extra_spaces_and_line_breaks__(self, text: str) -> str:
        '''
        Удаляет из строки лишние пробелы и переносы строки.\n
        text: строка.\n
        Возврщает строку, с удалёнными лишними пробелами и переносами строк.
        '''

        processed = ""

        if type(text) != str or len(text) == 0:
            return ""

        flag = True
        for symb in text:
            if flag and (symb == " " or symb == "\n"):
                processed += " "
                flag = False

            if symb != " " and symb != "\n":
                flag = True

            if flag:
                processed += symb

        return processed.strip()

    def __time_processing__(self, text: str) -> str:
        '''
        Обрабатывает строку, содержащую дату.\n
        text: строка, содержащая время в формате dd:dd.\n
        Возвращает вместо времени строку time.
        '''

        if re.match(r"\d{2}:\d{2}", text):
            return "time"
        else:
            return text.replace(":", "")

    def __processing_token__(self, token_lemma: str) -> str:
        '''
        Обрабатывает 1 терм.\n
        token_lemma: строка.\n
        Возвращает обработанный терм.
        '''

        return self.__time_processing__(
            self.__remove_extra_spaces_and_line_breaks__(token_lemma)
        )

    def __processing_cell__(self, cell: str) -> str:
        '''
        Полностью обрабатывает 1 ячейку pandas DataFrame. То есть проводит
        токенизацию, лемматизацию, удаление стоп слов и перевод в нижний регистр,
        потом происходит склейка и возвращается обработанная ячейка.\n
        cell: строка - ячейка pandas DataFrame.\n
        Возвращает обработанную строку.
        '''

        parts = self.__split_into_en_and_ru__(cell)

        tokens = []

        for part in parts:
            if part[0]:
                tokens += [
                    self.__processing_token__(token.lemma_)
                    for token in self.nlp_en(part[1])
                    if not (token.is_stop) and not (token.is_punct) and
                    len(self.__processing_token__(token.lemma_)) > 1
                ]
            else:
                tokens += [
                    self.__processing_token__(token.lemma_)
                    for token in self.nlp_ru(part[1])
                    if not (token.is_stop) and not (token.is_punct) and
                    len(self.__processing_token__(token.lemma_)) > 1
                ]

        return " ".join(tokens)

    def __processing__(
        self, data: pd.DataFrame, processing_columns: list[str]
    ) -> pd.DataFrame:
        '''
        Функция, вызывающая вышеописанные функции для обработки pandas DataFrame.\n
        data: pandas DataFrame;\n
        processing_columns: list[str] - список столбцов, которые нужно обрабатывать.\n
        Возвращает обработанный pandas DataFrame.
        '''

        p_data = data.copy(deep=True)
        p_data.fillna("", inplace=True)

        for column in processing_columns:
            for row in range(p_data.shape[0]):
                cell = p_data.loc[row, column]

                if type(cell) == str and len(cell) > 0:
                    p_data.loc[row, column] = self.__processing_cell__(
                        p_data.loc[row, column]
                    )
                else:
                    p_data.loc[row, column] = ""

        # return p_data[p_data.apply(
        #     lambda row: sum([len(cell)
        #                      for cell in row[processing_columns]]) > 0,
        #     axis=1
        # )].reset_index(drop=True)
        return p_data