import tkinter as tk
from tkinter import ttk
from typing import List, Tuple
from src.backend.index import My_search
import webbrowser


class SearchGUI:
    '''Класс графического интерфейса приложения.'''
    def __init__(self, master, search: My_search, indices_names: List[str]):
        '''Функция инициализации.

        Args:
            master: окно, в котором будет размещаться gui.
            search: экземпляр класса My_search для взаимодействия
            с Elasticsearch.
            indices_names: наименования индексов, которые присутствуют в
            Elasticsearch.'''
        self.master = master
        master.title("ElasticSearch Results")
        master.configure(bg='white')
        master.protocol("WM_DELETE_WINDOW", self.on_close)

        # Инициализация зависимостей
        self.search = search
        self.indices_names = indices_names

        # Параметры поиска
        self.fuzziness = 1
        self.num_of_responses = 15
        self.fields = ["title^2", "summary^2", "content"]

        # Инициализация UI
        self.create_search_frame()
        self.create_main_container()
        self.create_quick_answer_frame()
        self.create_results_frame()

        # Состояние UI
        self.loading_label = None
        self.answer_visible = False
        self.results_visible = False

    def create_main_container(self):
        '''Создает основной контейнер для контента'''
        self.main_frame = tk.Frame(self.master, bg='white')
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)

    def create_search_frame(self):
        '''Создает панель поиска'''
        search_frame = tk.Frame(self.master, bg='white')
        search_frame.pack(fill='x', padx=10, pady=10)

        self.entry = tk.Entry(search_frame, width=50)
        self.entry.pack(side='left', fill='x', expand=True, padx=(0, 5))

        search_btn = tk.Button(
            search_frame,
            text="🔍",
            command=self.perform_search,
            relief='flat',
            bg='white'
        )
        search_btn.pack(side='left')

    def perform_search(self):
        '''Обработчик поискового запроса'''
        try:
            self.show_loading()
            query = self.entry.get()

            # Выполнение поиска
            quick_answer, documents = self.search.search_for_gui(
                query=query,
                fields=self.fields,
                indices_names=self.indices_names,
                fuzziness=self.fuzziness,
                num_of_responses=self.num_of_responses
            )

            # Обновление интерфейса
            self.update_answer(quick_answer)
            self.update_documents(documents)

        except Exception as e:
            self.show_error(f"Ошибка поиска: {str(e)}")
        finally:
            self.hide_loading()

    def create_quick_answer_frame(self):
        '''Создает блок с быстрым ответом'''
        self.answer_frame = tk.Frame(
            self.main_frame,
            bd=2,
            relief='solid',
            bg='white',
            width=900,
            height=240
        )
        self.answer_frame.pack_propagate(False)

        # Упаковываем фрейм сразу, но управляем видимостью через прокси
        self.answer_frame.pack(pady=10, anchor='nw', fill='none')
        self.answer_frame.pack_forget()  # Сразу скрываем

        self.answer_text = tk.Text(
            self.answer_frame,
            wrap='word',
            bg='white',
            relief='flat',
            font=('Arial', 10),
            padx=10,
            pady=10,
            width=80,
            height=12
        )
        self.answer_text.pack(fill='both', expand=True)
        self.answer_text.insert('1.0', "Введите запрос...", 'left')
        self.answer_text.configure(state='disabled')

        self.toggle_visibility("answer", False)

    def create_results_frame(self):
        '''Создает блок с результатами поиска'''
        self.results_container = tk.Frame(self.main_frame, bg='white')

        # Настройка прокрутки
        self.canvas = tk.Canvas(
            self.results_container,
            bg='white',
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(
            self.results_container,
            orient='vertical',
            command=self.canvas.yview
        )

        # Прокручиваемая область
        self.scrollable_frame = tk.Frame(self.canvas, bg='white')
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def create_document_block(self, parent, link: str, content: str):
        '''Создает блок документа'''
        doc_frame = tk.Frame(
            parent,
            bd=1,
            relief='solid',
            bg='white'
        )
        doc_frame.pack(fill='x', pady=5, padx=2)

        # Содержание документа
        content_label = tk.Label(
            doc_frame,
            text=content,
            anchor='w',
            bg='white',
            wraplength=1200,
            justify='left',
            font=('Arial', 9)
        )
        content_label.pack(fill='x', padx=5, pady=(5, 0))

        # 3.2 Выравнивание по левому краю
        link_btn = tk.Button(
            doc_frame,
            text=link,
            fg='blue',
            cursor='hand2',
            command=lambda: webbrowser.open(link),
            relief='flat',
            bg='white',
            font=('Arial', 9, 'underline'),
            anchor='w',  # Выравнивание текста по левому краю
            justify='left'
        )
        link_btn.pack(fill='x', padx=5, pady=(0, 5), anchor='w')

    def update_answer(self, quick_answer: str):
        '''Обновляет блок с быстрым ответом'''
        self.answer_text.configure(state='normal')
        self.answer_text.delete('1.0', 'end')

        if quick_answer:
            self.answer_text.insert('1.0', quick_answer, "left")
            self.toggle_visibility("answer", True)
        else:
            self.toggle_visibility("answer", False)

        self.answer_text.configure(state='disabled')

    def update_documents(self, documents: List[Tuple[str, str]]):
        '''Обновляет результаты поиска'''
        # Очистка старых результатов
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Добавление новых результатов
        if documents:
            for link, content in documents:
                self.create_document_block(self.scrollable_frame, link, content)
            self.toggle_visibility("results", True)
        else:
            no_results = tk.Label(
                self.scrollable_frame,
                text="Ничего не найдено",
                bg='white',
                font=('Arial', 10)
            )
            no_results.pack(pady=20)
            self.toggle_visibility("results", True)

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def toggle_visibility(self, element: str, show: bool):
        '''Управляет видимостью элементов'''
        if element == "answer":
            if show:
                # Теперь фрейм всегда физически упакован, управляем только видимостью
                self.answer_frame.pack(side='top', pady=10, anchor='nw', fill='none')
                self.answer_frame.lift()  # Гарантируем положение поверх других элементов
            else:
                self.answer_frame.pack_forget()
            self.answer_visible = show

        elif element == "results":
            if show:
                self.results_container.pack(fill='both', expand=True)
            else:
                self.results_container.pack_forget()
            self.results_visible = show

    def show_loading(self):
        '''Показывает индикатор загрузки'''
        self.toggle_visibility("answer", False)
        self.toggle_visibility("results", False)

        self.loading_label = tk.Label(
            self.main_frame,
            text="Идет поиск...",
            bg='white',
            font=('Arial', 10)
        )
        self.loading_label.pack(pady=20)
        self.master.update()

    def hide_loading(self):
        '''Скрывает индикатор загрузки'''
        if self.loading_label:
            self.loading_label.pack_forget()
            self.master.update()

    def show_error(self, message: str):
        '''Показывает сообщение об ошибке'''
        error_frame = tk.Frame(self.main_frame, bg='#ffebee')
        tk.Label(
            error_frame,
            text=message,
            bg='#ffebee',
            fg='#b71c1c',
            font=('Arial', 10)
        ).pack(padx=10, pady=5)
        error_frame.pack(fill='x', pady=5)
        self.master.after(5000, error_frame.pack_forget)

    def on_close(self):
        '''Обработчик закрытия окна'''
        self.master.destroy()