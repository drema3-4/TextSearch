from src.processing_text import Prepare_Text
from elasticsearch import Elasticsearch
import pandas as pd
import re
from src.short_answer import get_short_answer
import asyncio


class My_search:
    def __init__(self, host: str):
        self.es = Elasticsearch(host)
        self.analyzer = Prepare_Text()

    def create_index(self, index_name: str, index_settings) -> None:
        if not self.es.indices.exists(index=index_name):
            self.es.indices.create(index=index_name, body=index_settings)
        else:
            print(
                "Индекс уже есть, если хотите его пересоздать, то сначала удалите его!"
            )

    def create_indices(self, indices_names: list[str], indices_settings) -> None:
        for index_name, index_settings in zip(indices_names, indices_settings):
            self.create_index(index_name, index_settings)

    def delete_index(self, index_name) -> None:
        if self.es.indices.exists(index=index_name):
            self.es.indices.delete(index=index_name)
        else:
            print("Такого индекса не существует!")

    def delete_indices(self, indices_names: list[str]) -> None:
        for index_name in indices_names:
            self.delete_index(index_name)

    def add_doc(self, doc: dict[str, str], indices_names: str, processing_fields: list[str]):
        custom_analyzer_doc = {}
        for field in doc:
            for field in processing_fields:
                custom_analyzer_doc[field] = self.analyzer.prepare_text(doc[field])
                custom_analyzer_doc[f"true_{field}"] = self.analyzer.light_prepare_text(doc[field])
            else:
                custom_analyzer_doc[field] = self.analyzer.light_prepare_text(doc[field])
                custom_analyzer_doc[f"true_{field}"] = self.analyzer.light_prepare_text(doc[field])

        for index_name in indices_names:
            if re.search("standart", index_name):
                self.es.index(index=index_name, document=doc)
            else:
                self.es.index(index=index_name, document=custom_analyzer_doc)

    def add_docs(
        self, path_excel_docs: str, indices_names: list[str], fields: list[str],
        processing_fields: list[str], num_of_docs: int
    ) -> None:
        docs = self.analyzer.prepare_docs(
            path=path_excel_docs,
            columns=fields,
            processing_columns=processing_fields,
            num_of_docs=num_of_docs
        )
        true_docs = self.analyzer.light_prepare_docs(path=path_excel_docs, columns=fields, num_of_docs=num_of_docs)
        true_docs = true_docs.fillna("")
        true_docs = true_docs.astype(str)

        for row in range(docs.shape[0]):
            custom_analyzer_doc = {}
            doc = {}
            for column in docs.columns:
                custom_analyzer_doc[column] = docs.loc[row, column]
                custom_analyzer_doc[f"true_{column}"] = true_docs.loc[row, column]
                doc[column] = true_docs.loc[row, column]

            for index_name in indices_names:
                if re.search("standart", index_name):
                    self.es.index(index=index_name, document=doc)
                else:
                    self.es.index(index=index_name, document=custom_analyzer_doc)

    def search_one_field_and_index(self, query: str, field: str, index_name: str, fuzziness: float = "AUTO", num_of_responses: int = 10):
        body = {
            "query": {
                "match": {
                    field: {
                        "query": self.analyzer.prepare_text(query),
                        "fuzziness": fuzziness
                    }
                }
            },
            "size": num_of_responses
        }

        results = self.es.search(index=index_name, body=body)

        print(f"Найдено документов: {results['hits']['total']['value']}")
        for hit in results["hits"]["hits"]:
            doc = hit["_source"]
            print("___________________________________________________")
            print("___________________________________________________")
            print(f"Index: {hit['_index']}, ID: {hit['_id']}, Score: {hit['_score']}")
            try:
                print(f"title: {doc["true_title"]}")
            except:
                print(f"title: {doc["title"]}")
            try:
                print(f"summary: {doc["true_summary"]}")
            except:
                print(f"title: {doc["summary"]}")
            try:
                print(f"content: {doc["true_content"]}")
            except:
                print(f"title: {doc["content"]}")

    def search_one_and_many_indices(self, query: str, field: str, indices_names: list[str], fuzziness: float = "AUTO", num_of_responses: int=10):
        body = {
            "query": {
                "match": {
                    field: {
                        "query": self.analyzer.prepare_text(query),
                        "fuzziness": fuzziness
                    }
                }
            },
            "size": num_of_responses
        }

        results = self.es.search(index=indices_names, body=body)

        print(f"Найдено документов: {results['hits']['total']['value']}")
        for hit in results["hits"]["hits"]:
            doc = hit["_source"]
            print("___________________________________________________")
            print("___________________________________________________")
            print(f"Index: {hit['_index']}, ID: {hit['_id']}, Score: {hit['_score']}")
            try:
                print(f"title: {doc["true_title"]}")
            except:
                print(f"title: {doc["title"]}")
            try:
                print(f"summary: {doc["true_summary"]}")
            except:
                print(f"title: {doc["summary"]}")
            try:
                print(f"content: {doc["true_content"]}")
            except:
                print(f"title: {doc["content"]}")

    def search_many_fields_one_index(self, query: str, fields: list[str], index_name: str, fuzziness: float = "AUTO", num_of_responses: int = 10):
        body = {
            "query": {
                "multi_match": {
                    "query": self.analyzer.prepare_text(query),
                    "fields": fields,
                    "fuzziness": fuzziness,
                    "type": "best_fields"
                }
            },
            "size": num_of_responses
        }

        results = self.es.search(index=index_name, body=body)

        print(f"Найдено документов: {results['hits']['total']['value']}")
        for hit in results["hits"]["hits"]:
            doc = hit["_source"]
            print("___________________________________________________")
            print("___________________________________________________")
            print(f"Index: {hit['_index']}, ID: {hit['_id']}, Score: {hit['_score']}")
            try:
                print(f"title: {doc["true_title"]}")
            except:
                print(f"title: {doc["title"]}")
            try:
                print(f"summary: {doc["true_summary"]}")
            except:
                print(f"title: {doc["summary"]}")
            try:
                print(f"content: {doc["true_content"]}")
            except:
                print(f"title: {doc["content"]}")

    def search_many_fields_many_indices(self, query: str, fields: list[str], indices_names: list[str], fuzziness: float = "AUTO", num_of_responses: int = 10):
        body = {
            "query": {
                "multi_match": {
                    "query": self.analyzer.prepare_text(query),
                    "fields": fields,
                    "fuzziness": fuzziness,
                    "type": "best_fields"
                }
            },
            "size": num_of_responses
        }

        results = self.es.search(index=indices_names, body=body)

        print(f"Найдено документов: {results['hits']['total']['value']}")
        for hit in results["hits"]["hits"]:
            doc = hit["_source"]
            print("___________________________________________________")
            print("___________________________________________________")
            print(f"Index: {hit['_index']}, ID: {hit['_id']}, Score: {hit['_score']}")
            try:
                print(f"title: {doc["true_title"]}")
            except:
                print(f"title: {doc["title"]}")
            try:
                print(f"summary: {doc["true_summary"]}")
            except:
                print(f"title: {doc["summary"]}")
            try:
                print(f"content: {doc["true_content"]}")
            except:
                print(f"title: {doc["content"]}")

    def __get_answer__(self, query: str, context_texts: list[str]):
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

    def search_many_fields_with_qa(self, query: str, fields: list[str], indices_names: list[str], fuzziness: float = "AUTO", num_of_responses: int = 10):
        body = {
            "query": {
                "multi_match": {
                    "query": self.analyzer.prepare_text(query),
                    "fields": fields,
                    "fuzziness": fuzziness,
                    "type": "best_fields"
                }
            },
            "size": num_of_responses
        }

        results = self.es.search(index=indices_names, body=body)

        contexts = []
        for hit in results['hits']['hits']:
            context = ""
            try:
                context = hit["_source"]["true_content"]
            except:
                context = hit["_source"]["content"]
            contexts.append(context)

        # print(f"Найдено документов: {results['hits']['total']['value']}")
        print("___________________________________________________")
        print("___________________________________________________")
        print("Answer:")
        print(self.__get_answer__(query=query, context_texts=contexts))
        print("___________________________________________________")
        for hit in results["hits"]["hits"]:
            doc = hit["_source"]
            print("___________________________________________________")
            print("___________________________________________________")
            print(f"Index: {hit['_index']}, ID: {hit['_id']}, Score: {hit['_score']}")
            try:
                print(f"title: {doc["true_title"]}")
            except:
                print(f"title: {doc["title"]}")
            try:
                print(f"summary: {doc["true_summary"]}")
            except:
                print(f"title: {doc["summary"]}")
            try:
                print(f"content: {doc["true_content"]}")
            except:
                print(f"title: {doc["content"]}")

    def search_for_gui(self, query: str, fields: list[str], indices_names: list[str], fuzziness: float = "AUTO", num_of_responses: int = 10) -> (str, list[(str, str)]):
        body = {
            "query": {
                "multi_match": {
                    "query": self.analyzer.prepare_text(query),
                    "fields": fields,
                    "fuzziness": fuzziness,
                    "type": "best_fields"
                }
            },
            "size": num_of_responses
        }

        results = self.es.search(index=indices_names, body=body)

        contexts = []
        for hit in results['hits']['hits']:
            context = ""
            try:
                context = hit["_source"]["true_content"]
            except:
                context = hit["_source"]["content"]
            contexts.append(context)


        quick_answer = self.__get_answer__(query=query, context_texts=contexts)
        documents = []

        for hit in results["hits"]["hits"]:
            doc = hit["_source"]
            try:
                documents.append((doc["url"], doc["true_summary"]))
            except:
                documents.append((doc["url"], doc["summary"]))

        return quick_answer, documents