from src.backend.processing_text import Prepare_Text
from elasticsearch import Elasticsearch
import re
from src.backend.short_answer import get_short_answer
import asyncio
from sentence_transformers import SentenceTransformer


class My_search:
    '''Класс для работы с Elasticsearch: создание индексов и работа с ними:
    вставка, удаление, поиск.'''
    def __init__(self, host: str):
        '''Функция инициализации. Подключаемся к
        Elasticsearch и создаём класс обработчик текста.

        Args:
            host: http ссылка на Elasticsearch.'''
        self.es = Elasticsearch(host)
        self.analyzer = Prepare_Text()
        self.maker_embedding = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

    def create_index(self, index_name: str, index_settings) -> None:
        '''Создание нового индекса в Elasticsearch.

        Args:
            index_name: наименование индекса.
            index_settings: настройки индекса по Elasticsearch нотации.'''
        if not self.es.indices.exists(index=index_name):
            self.es.indices.create(index=index_name, body=index_settings)
        else:
            print(
                "Индекс уже есть, если хотите его пересоздать, то сначала удалите его!"
            )

    def create_indices(self, indices_names: list[str], indices_settings) -> None:
        '''Создание нескольких индексов. Просто цикличное применение
        функции по созданию одного индекса.

        Args:
            indices_names: список наименований индексов.
            indices_settings: список настроек индексов (для каждого индекса
            один набор настроек).'''
        for index_name, index_settings in zip(indices_names, indices_settings):
            self.create_index(index_name, index_settings)

    def delete_index(self, index_name) -> None:
        '''Удаление индекса из Elasticsearch.

        Args:
            index_name: наименование индекса, который нужно удалить.'''
        if self.es.indices.exists(index=index_name):
            self.es.indices.delete(index=index_name)
        else:
            print("Такого индекса не существует!")

    def delete_indices(self, indices_names: list[str]) -> None:
        '''Удаление индексов. Просто цикличное применение функции
        по удалению одного индекса.

        Args:
            indices_names: список наименований индексов, которые
            нужно удалить.'''
        for index_name in indices_names:
            self.delete_index(index_name)

    def add_doc(self, doc: dict[str, str], indices_names: list[str], processing_fields: list[str]) -> None:
        '''Добавление одного документа в индексы Elasticsearch.

        Args:
            doc: словарь (поле, значение), которые представляет сам документ,
            важно, чтобы соответствующие поля были в индексе.
            indices_names: наименования индексов, в которые нужно добавить
            документ.
            processing_fields: наименование полей документа, которые нужно
            подготовить перед вставкой в индекс.'''
        custom_analyzer_doc = {}
        for field in doc:
            for field in processing_fields:
                custom_analyzer_doc[field] = self.analyzer.prepare_text(doc[field])
                custom_analyzer_doc[f"true_{field}"] = self.analyzer.light_prepare_text(doc[field])
            else:
                custom_analyzer_doc[field] = self.analyzer.light_prepare_text(doc[field])
                custom_analyzer_doc[f"true_{field}"] = self.analyzer.light_prepare_text(doc[field])

        doc["content_embedding"] = self.maker_embedding.encode(doc["content"]).tolist()
        custom_analyzer_doc["content_embedding"] = self.maker_embedding.encode(custom_analyzer_doc["content"]).tolist()

        for index_name in indices_names:
            if re.search("standart", index_name):
                self.es.index(index=index_name, document=doc)
            else:
                self.es.index(index=index_name, document=custom_analyzer_doc)

    def add_docs(
        self, path_excel_docs: str, indices_names: list[str], fields: list[str],
        processing_fields: list[str], num_of_docs: int
    ) -> None:
        '''Добавления массива документов, представленных в excel формате.

        Args:
            path_excel_docs: путь к excel файлу с документами.
            indices_names: наименования индексов, в которые нужно загрузить
            документы.
            fields: поля документов (столбы в excel таблице), которые нужно
            загружать.
            processing_fields: поля документов, которые необходимо подготовить
            перед загрузкой.
            num_of_docs: количество документов (строк), которые необходимо загрузить.'''
        docs = self.analyzer.prepare_docs(
            path=path_excel_docs,
            columns=fields,
            processing_columns=processing_fields,
            num_of_docs=num_of_docs
        )
        true_docs = self.analyzer.light_prepare_docs(
            path=path_excel_docs,
            columns=fields,
            num_of_docs=num_of_docs
        )
        true_docs = true_docs.fillna("")
        true_docs = true_docs.astype(str)

        # Заменяем оставшиеся NaN значения пустой строкой
        true_docs = true_docs.fillna("")
        true_docs = true_docs.astype(str)
        true_docs = true_docs.replace(['nan', 'NaN', 'null', 'None'], '',
                                      regex=True)  # Добавляем замену строковых представлений

        docs = docs.fillna("")
        docs = docs.astype(str)
        docs = docs.replace(['nan', 'NaN', 'null', 'None'], '', regex=True)  # Обрабатываем также основной DataFrame

        for row in range(docs.shape[0]):
            custom_analyzer_doc = {}
            doc = {}
            for column in docs.columns:
                custom_analyzer_doc[column] = docs.loc[row, column]
                custom_analyzer_doc[f"true_{column}"] = true_docs.loc[row, column]
                doc[column] = true_docs.loc[row, column]


            doc["content_embedding"] = self.maker_embedding.encode(doc["content"] if type(doc["content"]) == str else "").tolist()
            custom_analyzer_doc["content_embedding"] = self.maker_embedding.encode(custom_analyzer_doc["content"] if type(custom_analyzer_doc["content"]) == str else "").tolist()

            for index_name in indices_names:
                if re.search("standart", index_name):
                    self.es.index(index=index_name, document=doc)
                else:
                    self.es.index(index=index_name, document=custom_analyzer_doc)
## Устаревшая функция
    # def search_many_fields_many_indices(
    #     self,
    #     query: str,
    #     fields: list[str],
    #     indices_names: list[str],
    #     fuzziness: float = "AUTO",
    #     num_of_responses: int = 10
    # ) -> None:
    #     '''Поиск по нескольким (одному) полям и нескольким (одному) индексам.
    #
    #     Args:
    #         query: запрос, по которому нужно найти информацию.
    #         fields: наименования полей, по которым нужно производить поиск.
    #         indices_names: наименования индексов, в которых необходимо производить поиск.
    #         fuzziness: количество ошибок, которое можно сделать при сопоставлении слов.
    #         num_of_responses: количество ответов, которые нужно вывести в качестве ответа
    #         на запрос.'''
    #     body = {
    #         "query": {
    #             "multi_match": {
    #                 "query": self.analyzer.prepare_text(query),
    #                 "fields": fields,
    #                 "fuzziness": fuzziness,
    #                 "type": "best_fields"
    #             }
    #         },
    #         "size": num_of_responses
    #     }
    #
    #     results = self.es.search(index=indices_names, body=body)
    #
    #     print(f"Найдено документов: {results['hits']['total']['value']}")
    #     for hit in results["hits"]["hits"]:
    #         doc = hit["_source"]
    #         print("___________________________________________________")
    #         print("___________________________________________________")
    #         print(f"Index: {hit['_index']}, ID: {hit['_id']}, Score: {hit['_score']}")
    #         try:
    #             print(f"title: {doc["true_title"]}")
    #         except:
    #             print(f"title: {doc["title"]}")
    #         try:
    #             print(f"summary: {doc["true_summary"]}")
    #         except:
    #             print(f"title: {doc["summary"]}")
    #         try:
    #             print(f"content: {doc["true_content"]}")
    #         except:
    #             print(f"title: {doc["content"]}")

    def __get_answer__(
        self,
        query: str,
        context_texts: list[str]
    ) -> str:
        '''Формирование краткого ответа по запросу на основе поисковой выдачи.

        Args:
            query: запрос, на который нужно сформировать ответ.
            context_texts: поисковая выдача.

        Returns:
            str: строка, в которой содержится ответ на вопрос пользователя,
            сформированный при помощи YandexGpt.'''
        prompt_get_answer = "Ты внимательно анализируешь предоставленные документы и точно отвечаешь на вопросы по ним. Если нужной информации нет, то в качестве ответа напиши только число 0 и ничего больше."
        prompt_compare_answers = "На каждой строке тебе дан один вариант ответа, ты внимательно анализируешь их на соответствие вопросу и возвращаешь лучший из них, только его."

        answers = []
        for text in context_texts:
            try:
                answer = asyncio.run(get_short_answer(prompt_get_answer, text, query))
                if answer != "0":
                    answers.append(answer)
            except:
                continue

        if answers:
            answers_for_query = ""
            for answer in answers:
                answers_for_query += answer + "\n"
            return asyncio.run(get_short_answer(prompt_compare_answers, answers_for_query, query))

        return "0"

## Устаревшая функция
    # def search_many_fields_with_qa(
    #     self,
    #     query: str,
    #     fields: list[str],
    #     indices_names: list[str],
    #     fuzziness: float = "AUTO",
    #     num_of_responses: int = 10
    # ) -> None:
    #     '''Поиск по нескольким (одному) полям и нескольким (одному) индексам.
    #     + к ответу добавляется ответ YandexGpt, сформированный на основе
    #     полученной поисковой выдачи.
    #
    #     Args:
    #         query: запрос, по которому нужно найти информацию.
    #         fields: наименования полей, по которым нужно производить поиск.
    #         indices_names: наименования индексов, в которых необходимо производить поиск.
    #         fuzziness: количество ошибок, которое можно сделать при сопоставлении слов.
    #         num_of_responses: количество ответов, которые нужно вывести в качестве ответа
    #         на запрос.'''
    #     body = {
    #         "query": {
    #             "multi_match": {
    #                 "query": self.analyzer.prepare_text(query),
    #                 "fields": fields,
    #                 "fuzziness": fuzziness,
    #                 "type": "best_fields"
    #             }
    #         },
    #         "size": num_of_responses
    #     }
    #
    #     results = self.es.search(index=indices_names, body=body)
    #
    #     contexts = []
    #     for hit in results['hits']['hits']:
    #         context = ""
    #         try:
    #             context = hit["_source"]["true_content"]
    #         except:
    #             context = hit["_source"]["content"]
    #         contexts.append(context)
    #
    #     # print(f"Найдено документов: {results['hits']['total']['value']}")
    #     print("___________________________________________________")
    #     print("___________________________________________________")
    #     print("Answer:")
    #     print(self.__get_answer__(query=query, context_texts=contexts))
    #     print("___________________________________________________")
    #     for hit in results["hits"]["hits"]:
    #         doc = hit["_source"]
    #         print("___________________________________________________")
    #         print("___________________________________________________")
    #         print(f"Index: {hit['_index']}, ID: {hit['_id']}, Score: {hit['_score']}")
    #         try:
    #             print(f"title: {doc["true_title"]}")
    #         except:
    #             print(f"title: {doc["title"]}")
    #         try:
    #             print(f"summary: {doc["true_summary"]}")
    #         except:
    #             print(f"title: {doc["summary"]}")
    #         try:
    #             print(f"content: {doc["true_content"]}")
    #         except:
    #             print(f"title: {doc["content"]}")

    def search_for_gui(
            self,
            query: str,
            fields: list[str],
            indices_names: list[str],
            fuzziness: float = "AUTO",
            num_of_responses: int = 10
    ) -> (str, list[(str, str)]):
        '''Функция формирования ответа для вывода его в gui.

        Args:
            query: запрос, по которому нужно найти информацию.
            fields: наименования полей, по которым нужно производить поиск.
            indices_names: наименования индексов, в которых необходимо производить поиск.
            fuzziness: количество ошибок, которое можно сделать при сопоставлении слов.
            num_of_responses: количество ответов, которые нужно вывести в качестве ответа
            на запрос.

        Returns:
            (str, list[(str, str)]): возвращает кортеж (краткий ответ, сформированный gpt;
            поисковая выдача).'''
        query = self.analyzer.prepare_text(query)
        query_embedding = self.maker_embedding.encode(query).tolist()

        # 1. BM25 запрос
        bm25_query = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": fields,
                    "fuzziness": fuzziness,
                    "type": "best_fields"
                }
            },
            "size": num_of_responses * 2
        }

        # 2. kNN запрос
        knn_query = {
            "knn": {
                "field": "content_embedding",
                "query_vector": query_embedding,
                "k": num_of_responses * 2,
                "num_candidates": 100
            },
            "size": num_of_responses * 2
        }

        # 3. Выполняем оба запроса
        bm25_results = self.es.search(index=indices_names, body=bm25_query)
        knn_results = self.es.search(index=indices_names, body=knn_query)

        # 4. Применяем RRF вручную и собираем полные документы
        def manual_rrf(bm25_hits, knn_hits, rank_constant=20):
            scores = {}
            docs = {}  # Будем хранить документы здесь

            # Обрабатываем BM25 результаты
            for rank, hit in enumerate(bm25_hits, 1):
                doc_id = hit["_id"]
                scores[doc_id] = scores.get(doc_id, 0) + 1 / (rank + rank_constant)
                docs[doc_id] = hit  # Сохраняем документ

            # Обрабатываем kNN результаты
            for rank, hit in enumerate(knn_hits, 1):
                doc_id = hit["_id"]
                scores[doc_id] = scores.get(doc_id, 0) + 1 / (rank + rank_constant)
                if doc_id not in docs:  # Сохраняем документ, если его еще нет
                    docs[doc_id] = hit

            # Сортируем по убыванию RRF-оценки
            sorted_ids = sorted(scores.items(), key=lambda x: x[1], reverse=True)

            # Возвращаем документы в нужном порядке
            return [(docs[doc_id], score) for doc_id, score in sorted_ids]

        final_results = manual_rrf(
            bm25_results["hits"]["hits"],
            knn_results["hits"]["hits"]
        )[:num_of_responses]

        contexts = []
        for hit, score in final_results:
            context = ""
            try:
                context = hit["_source"]["true_content"]
            except:
                context = hit["_source"]["content"]
            contexts.append(context)

        quick_answer = self.__get_answer__(query=query, context_texts=contexts)
        documents = []

        for hit, score in final_results:
            doc = hit["_source"]
            try:
                documents.append((doc["url"], doc["true_summary"]))
            except:
                documents.append((doc["url"], doc["summary"]))

        return quick_answer, documents

    # def search_for_gui(
    #     self,
    #     query: str,
    #     fields: list[str],
    #     indices_names: list[str],
    #     fuzziness: float = "AUTO",
    #     num_of_responses: int = 10
    # ) -> (str, list[(str, str)]):
    #     '''Функция формирования ответа для вывода его в gui.
    #
    #     Args:
    #         query: запрос, по которому нужно найти информацию.
    #         fields: наименования полей, по которым нужно производить поиск.
    #         indices_names: наименования индексов, в которых необходимо производить поиск.
    #         fuzziness: количество ошибок, которое можно сделать при сопоставлении слов.
    #         num_of_responses: количество ответов, которые нужно вывести в качестве ответа
    #         на запрос.
    #
    #     Returns:
    #         (str, list[(str, str)]): возвращает кортеж (краткий ответ, сформированный gpt;
    #         поисковая выдача).'''
    #     body = {
    #         "query": {
    #             "multi_match": {
    #                 "query": self.analyzer.prepare_text(query),
    #                 "fields": fields,
    #                 "fuzziness": fuzziness,
    #                 "type": "best_fields"
    #             }
    #         },
    #         "size": num_of_responses
    #     }
    #
    #     results = self.es.search(index=indices_names, body=body)
    #
    #     contexts = []
    #     for hit in results['hits']['hits']:
    #         context = ""
    #         try:
    #             context = hit["_source"]["true_content"]
    #         except:
    #             context = hit["_source"]["content"]
    #         contexts.append(context)
    #
    #
    #     quick_answer = self.__get_answer__(query=query, context_texts=contexts)
    #     documents = []
    #
    #     for hit in results["hits"]["hits"]:
    #         doc = hit["_source"]
    #         try:
    #             documents.append((doc["url"], doc["true_summary"]))
    #         except:
    #             documents.append((doc["url"], doc["summary"]))
    #
    #     return quick_answer, documents