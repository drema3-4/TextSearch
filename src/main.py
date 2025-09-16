from src.backend.index import My_search
from src.frontend.gui import *

HOST = "http://localhost:9200"
INDICES_NAMES = [
    "my_index_standart_analyzer",
    "my_index_standart_analyzer_ngramms",
    "my_index_custom_analyzer",
    "my_index_custom_analyzer_ngramms",
]
root = tk.Tk()
app = SearchGUI(
    master=root,
    search=My_search(host=HOST),
    indices_names=INDICES_NAMES
)
root.geometry("1280x720")
root.mainloop()

# DATA_PATH = "../news.xlsx"
# COLUMNS = ["url", "title", "summary", "content", "tags"]
# PROCESSING_COLUMNS = ["title", "summary", "content", "tags"]
# HOST = "http://localhost:9200"
# NUM_OF_DOCS = 10000
#
# INDICES_NAMES = [
#     "my_index_standart_analyzer",
#     "my_index_standart_analyzer_ngramms",
#     "my_index_custom_analyzer",
#     "my_index_custom_analyzer_ngramms",
# ]
# index_settings_standart_analyzer = {
#     "settings": {
#         "number_of_shards": 1,
#         "number_of_replicas": 0,
#         "analysis": {
#             "analyzer": {
#                 "my_analyzer": {
#                     "type": "custom",
#                     "tokenizer": "standard",
#                     "filter": [
#                         "lowercase",
#                         "russian_stop",
#                         "russian_stemmer"
#                     ]
#                 }
#             },
#             "filter": {
#                 "russian_stop": {
#                     "type": "stop",
#                     "stopwords": "_russian_"
#                 },
#                 "russian_stemmer": {
#                     "type": "stemmer",
#                     "language": "russian"
#                 }
#             }
#         }
#     },
#     "mappings": {
#         "properties": {
#             "url": {
#                 "type": "text"
#             },
#             "title": {
#                 "type": "text",
#                 "analyzer": "my_analyzer",
#                 "search_analyzer": "my_analyzer"
#             },
#             "summary": {
#                 "type": "text",
#                 "analyzer": "my_analyzer",
#                 "search_analyzer": "my_analyzer"
#             },
#             "content": {
#                 "type": "text",
#                 "analyzer": "my_analyzer",
#                 "search_analyzer": "my_analyzer"
#             },
#             "tags": {
#                 "type": "text",
#                 "analyzer": "my_analyzer",
#                 "search_analyzer": "my_analyzer"
#             },
#             "content_embedding": {
#                 "type": "dense_vector",
#                 "dims": 384,
#                 "index": True,
#                 "similarity": "cosine"
#             }
#         }
#     }
# }
# index_settings_standart_analyzer_ngramms = {
#     "settings": {
#         "number_of_shards": 1,
#         "number_of_replicas": 0,
#         "index": {
#             "max_ngram_diff": 2
#         },
#         "analysis": {
#             "analyzer": {
#                 "ngram_analyzer": {
#                     "type": "custom",
#                     "tokenizer": "ngram_tokenizer",
#                     "filter": [
#                         "lowercase",
#                         "russian_stop",
#                         "russian_stemmer"
#                     ]
#                 }
#             },
#             "filter": {
#                 "russian_stop": {
#                     "type": "stop",
#                     "stopwords": "_russian_"
#                 },
#                 "russian_stemmer": {
#                     "type": "stemmer",
#                     "language": "russian"
#                 }
#             },
#             "tokenizer": {
#                 "ngram_tokenizer": {
#                     "type": "ngram",
#                     "min_gram": 1,
#                     "max_gram": 3,
#                     "token_chars": ["letter", "digit"]
#                 }
#             }
#         }
#     },
#     "mappings": {
#         "properties": {
#             "url": {
#                 "type": "text"
#             },
#             "title": {
#                 "type": "text",
#                 "analyzer": "ngram_analyzer",
#                 "search_analyzer": "ngram_analyzer"
#             },
#             "summary": {
#                 "type": "text",
#                 "analyzer": "ngram_analyzer",
#                 "search_analyzer": "ngram_analyzer"
#             },
#             "content": {
#                 "type": "text",
#                 "analyzer": "ngram_analyzer",
#                 "search_analyzer": "ngram_analyzer"
#             },
#             "tags": {
#                 "type": "text",
#                 "analyzer": "ngram_analyzer",
#                 "search_analyzer": "ngram_analyzer"
#             },
#             "content_embedding": {
#                 "type": "dense_vector",
#                 "dims": 384,
#                 "index": True,
#                 "similarity": "cosine"
#             }
#         }
#     }
# }
# index_settings_custom_analyzer = {
#     "settings": {
#         "number_of_shards": 1,
#         "number_of_replicas": 0
#     },
#     "mappings": {
#         "properties": {
#             "url": {
#                 "type": "text"
#             },
#             "title": {
#                 "type": "text"
#             },
#             "true_title": {
#                 "type": "text"
#             },
#             "summary": {
#                 "type": "text"
#             },
#             "true_summary": {
#                 "type": "text"
#             },
#             "content": {
#                 "type": "text"
#             },
#             "true_content": {
#                 "type": "text"
#             },
#             "tags": {
#                 "type": "text"
#             },
#             "true_tags": {
#                 "type": "text"
#             },
#             "content_embedding": {
#                 "type": "dense_vector",
#                 "dims": 384,
#                 "index": True,
#                 "similarity": "cosine"
#             }
#         }
#     }
# }
# index_settings_custom_analyzer_ngramms = {
#     "settings": {
#         "number_of_shards": 1,
#         "number_of_replicas": 0,
#         "index": {
#             "max_ngram_diff": 2
#         },
#         "analysis": {
#             "analyzer": {
#                 "ngram_analyzer": {
#                     "tokenizer": "ngram_tokenizer"
#                 }
#             },
#             "tokenizer": {
#                 "ngram_tokenizer": {
#                     "type": "ngram",
#                     "min_gram": 1,
#                     "max_gram": 3,
#                     "token_chars": ["letter", "digit"]
#                 }
#             }
#         }
#     },
#     "mappings": {
#         "properties": {
#             "url": {
#                 "type": "text"
#             },
#             "title": {
#                 "type": "text",
#                 "analyzer": "ngram_analyzer",
#                 "search_analyzer": "ngram_analyzer"
#             },
#             "true_title": {
#                 "type": "text"
#             },
#             "summary": {
#                 "type": "text",
#                 "analyzer": "ngram_analyzer",
#                 "search_analyzer": "ngram_analyzer"
#             },
#             "true_summary": {
#                 "type": "text"
#             },
#             "content": {
#                 "type": "text",
#                 "analyzer": "ngram_analyzer",
#                 "search_analyzer": "ngram_analyzer"
#             },
#             "true_content": {
#                 "type": "text"
#             },
#             "tags": {
#                 "type": "text",
#                 "analyzer": "ngram_analyzer",
#                 "search_analyzer": "ngram_analyzer"
#             },
#             "true_tags": {
#                 "type": "text"
#             },
#             "content_embedding": {
#                 "type": "dense_vector",
#                 "dims": 384,
#                 "index": True,
#                 "similarity": "cosine"
#             }
#         }
#     }
# }
# INDICES_SETTINGS = [
#     index_settings_standart_analyzer,
#     index_settings_standart_analyzer_ngramms,
#     index_settings_custom_analyzer,
#     index_settings_custom_analyzer_ngramms
# ]
#
# sr = My_search(host=HOST)


# def init() -> None:
#     sr.delete_indices(indices_names=INDICES_NAMES)
#     sr.create_indices(indices_names=INDICES_NAMES, indices_settings=INDICES_SETTINGS)
#
#     sr.add_docs(
#         path_excel_docs=DATA_PATH,
#         indices_names=INDICES_NAMES,
#         fields=COLUMNS,
#         processing_fields=PROCESSING_COLUMNS,
#         num_of_docs=NUM_OF_DOCS
#     )

# while True:
#     user_input = input("Введите команду\n>>> ")
#
#     if user_input.strip() == "help":
#         print(
#             "Чтобы выполнить поиск по одному полю введите <<one field>>\nЧтобы выполнить поиск по нескольким полям введите <<many fields>>\nЧтобы завершить работу введите <<stop>>\nДоступные поля: name, short_content, content, tags"
#         )
## Устаревшая часть
    # if user_input.strip() == "mfmi":
    #     # fields = input(
    #     #     "Введите поля, по которым будет производиться поиск\n>> "
    #     # ).split(" ")
    #     # num_of_responses = int(
    #     #     input("Введите количество ответов, которые хотите получить\n>> ")
    #     # )
    #     fuzziness = float(
    #         input(
    #             "Введите количество ошибок, которые можно делать при сопоставлении слов\n>> "
    #         )
    #     )
    #
    #     fields = ["title^2", "summary^2", "content"]
    #     num_of_responses = 10
    #
    #     query = input("Введите ваш запрос\n>> ")
    #     sr.search_many_fields_many_indices(
    #         query=query,
    #         fields=fields,
    #         indices_names=INDICES_NAMES,
    #         fuzziness=fuzziness,
    #         num_of_responses=num_of_responses
    #     )
## Устаревшая часть
    # if user_input.strip() == "qa":
    #     fuzziness = float(
    #         input(
    #             "Введите количество ошибок, которые можно делать при сопоставлении слов\n>> "
    #         )
    #     )
    #
    #     fields = ["title^2", "summary^2", "content"]
    #     num_of_responses = 10
    #
    #     query = input("Введите ваш запрос\n>> ")
    #     sr.search_many_fields_with_qa(
    #         query=query,
    #         fields=fields,
    #         indices_names=INDICES_NAMES,
    #         fuzziness=fuzziness,
    #         num_of_responses=num_of_responses
    #     )

    # if user_input.strip() == "stop":
    #     break
    #
    # if user_input.strip() == "init":
    #     init()