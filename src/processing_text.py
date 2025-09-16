import pandas as pd
import re
import string
import spacy
import numpy as np

class Prepare_Text:
    '''Класс для подготовки текста перед загрузкой его в индекс.

    Есть два вида подготовки:
        1. Лёгкая версия: очитска от лишних пробелов и переносов строк;
        2. Полновесная версия: легкая версия + токенизация, очистка от стоп-слов, очистка от неалфавитных токенов.'''
    def __init__(self):
        '''Функция инициализации.

        Загружает языковые пакеты библиотеки SpaCy.'''
        self.nlp_en = spacy.load("en_core_web_sm")
        self.nlp_ru = spacy.load("ru_core_news_sm")

    def light_prepare_text(self, text: str) -> str:
        '''Функция для облегчённой подготовки (удаление лишних пробелов
        и переносов строк) строки.

        Args:
            text: строка, которую нужно подготовить.

        Returns:
            str: подготовленная строка (без лишних пробелов и переносов строк).'''
        if type(text) == str and len(text) > 0:
            return self.__remove_extra_spaces_and_line_breaks__(text)
        else:
            return ""

    def light_prepare_docs(
        self, path: str, columns: list[str], num_of_docs: int
    ) -> pd.DataFrame:
        '''Функция для облегчённого варианта подготовки (удаление лишних
        пробелов и переносов строк) pandas DataFrame.

        Args:
            path: путь к файлу (формата excel) для загрузки его в
            pandas DataFrame.
            columns: столбцы, которые нужно будет загрузить в pandas DataFrame.
            num_of_docs: количество строк, которые нужно будет загрузить в
            pandas DataFrame.

        Returns:
            pd.DataFrame: возвращает подготовленный DataFrame, не содержащий
            пустых строк.'''
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

        docs = docs.replace(['', ' '], np.nan).dropna(how='all').reset_index(drop=True)

        return docs

    def prepare_text(self, text: str) -> str:
        '''Функция для полноценной подготовки одной строки.

        Args:
            text: строка, которую нужно будет подготовить.

        Returns:
            str: возвращает подготовленную функцией __processing__ строку.'''
        return self.__processing_cell__(text)

    def prepare_docs(
        self, path: str, columns: list[str], processing_columns: list[str],
        num_of_docs: int
    ) -> pd.DataFrame:
        '''Функция вызова обработки pandas DataFrame.

            Args:
                path: путь к файлу с данными (в формате excel), которые
                будут загружены в pandas DataFrame.
                columns: список столбцов, которые нужно загрузить из файла.
                processing_columns: список столбцов, которые нужно будет
                обработать в pandas DataFrame.
                num_of_docs: сколько строк загрузить из файла.

            Returns:
                pd.DataFrame: возвращает pandas DataFrame, подготовленный функцией
                __processing__.'''
        docs = pd.read_excel(path)
        docs = docs.loc[:num_of_docs, columns]
        docs = docs.fillna("")
        docs = docs.astype(str)

        return self.__processing__(docs, processing_columns)



    def __first_is_en__(self, cell: str) -> bool:
        '''Функция определяет алфавит первого символа строки.

        Args:
            cell: строка, для которой будут происходить вычисления.

        Returns:
            bool: возвращает True, если первый символ принадлежит английскому алфавиту,
            False в противном случае.'''
        index_first_en = re.search(r"[a-zA-Z]", cell)
        index_first_ru = re.search(r"[а-яА-Я]", cell)

        return True if index_first_en and (
            not (index_first_ru) or
            index_first_ru and index_first_en.start() < index_first_ru.start()
        ) else False

    def __split_into_en_and_ru__(self, cell: str) -> list[(bool, str)]:
        '''Разделяет строку на части, состоящие только из одного алфавита (русского
        или английскому.

        Args:
            cell: строка, которая будет разбиваться на части.

        Returns:
            list[(bool, str)]: (True (если алфавит английский), подстрока строки).
            В виде результата возвращается массив кортежей, в которых первое значение
            указывает тип алфавита строки, а второе содержит подстроку исходной строки.'''
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
        '''Удаляет из строки лишние пробелы и переносы строк, приводя её к
        читабельному виду.

        Args:
            text: строка, которая будет очищаться.

        Returns:
            str: возвращает очищенную от лишних пробелов и переносов строку.'''
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

    def __processing_cell__(self, cell: str) -> str:
        '''Обработка одной ячейки pandas DataFrame.

        Args:
            cell: ячейка pandas DataFrame (предполагаемо строкового типа.

        Returns:
            str: возвращает строку, очищенную от лишних пробелов и переносов
            строк + без стоп-слов, кроме того текст, кроме наименований,
            переводится в начальную форму и нижний регистр.'''
        parts = self.__split_into_en_and_ru__(
            self.__remove_extra_spaces_and_line_breaks__(cell)
        )

        tokens = []

        for part in parts:
            if part[0]:
                tokens += [
                    token.lemma_
                    for token in self.nlp_en(part[1])
                    if not (token.is_stop) and not (token.is_punct) and
                    len(token.lemma_) > 1
                ]
            else:
                tokens += [
                    token.lemma_
                    for token in self.nlp_ru(part[1])
                    if not (token.is_stop) and not (token.is_punct) and
                    len(token.lemma_) > 1
                ]

        return " ".join(tokens) if tokens else ""

    def __processing__(
        self, data: pd.DataFrame, processing_columns: list[str]
    ) -> pd.DataFrame:
        '''Обработка целого pandas DataFrame.

        Args:
            data: pandas DataFrame, который нужно обработать.
            processing_columns: список наименований столбцов pandas DataFrame,
            которые нужно обработать.

        Returns:
            pd.DataFrame: Возвращает pandas DataFrame, ячейки которого (только
            столбцов processing_columns) подготовлены функцией __processing_sell__.
            Строки, которые окажутся пустыми после очистки будут удалены.'''

        p_data = data.copy(deep=True)
        p_data.fillna("", inplace=True)

        for row in range(p_data.shape[0]):
            for column in processing_columns:
                p_data.loc[row, column] = self.__processing_cell__(p_data.loc[row, column])

        p_data = p_data.replace(['', ' '], np.nan).dropna(how='all').reset_index(drop=True)

        return p_data