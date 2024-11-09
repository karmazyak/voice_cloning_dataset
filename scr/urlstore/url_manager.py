import pandas as pd

class UrlManager:
    """
    Класс для управления списком урлов с дополнительной информацией.

    Параметры:
        - file_path (str): Путь к файлу для хранения данных.

    Атрибуты:
        - file_path (str): Путь к файлу для хранения данных.
        - df (pd.DataFrame): DataFrame для хранения урлов и связанных данных.

    Методы:
        - load_urls(): Загружает данные из файла, если он существует.
        - save_urls(): Сохраняет данные в файл.
        - add_urls(urls: List[dict], author: str): Добавляет массив урлов с указанными параметрами и автором.
        - get_all_urls(): Возвращает DataFrame со всеми урлами и их параметрами.
        - initialize_from_df(df: pd.DataFrame): Инициализирует объект из переданного DataFrame.
    """
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = pd.DataFrame(columns=['url', 'quality', 'source', 'author'])
        self.load_urls()

    def load_urls(self):
        """
        Загружает данные из файла, если файл существует.
        Если файла нет, создает пустой DataFrame.
        """
        try:
            self.df = pd.read_csv(self.file_path)
        except FileNotFoundError:
            pass

    def save_urls(self):
        """
        Сохраняет данные в файл.
        """
        self.df.to_csv(self.file_path, index=False)

    def add_urls(self, urls, author):
        """
        Добавляет массив урлов с указанными параметрами и автором.

        Параметры:
            - urls (List[dict]): Массив словарей, где каждый словарь содержит 'url', 'quality', 'source'.
            - author (str): Автор, добавляющий урлы.
        """
        for url_info in urls:
            url_exists = self.df['url'].str.contains(url_info['url']).any()
            if not url_exists:
                url_info['author'] = author
                new_row = pd.DataFrame([url_info], columns=['url', 'quality', 'source', 'author'])
                self.df = pd.concat([self.df, new_row], ignore_index=True)
        self.save_urls()

    def get_all_urls(self):
        """
        Возвращает DataFrame со всеми урлами и их параметрами.

        Возвращает:
            pd.DataFrame: DataFrame со столбцами 'url', 'quality', 'source', 'author'.
        """
        return self.df[['url', 'quality', 'source', 'author']]

    @classmethod
    def initialize_from_df(cls, df, file_path):
        """
        Инициализирует объект из переданного DataFrame.

        Параметры:
            - df (pd.DataFrame): DataFrame с данными урлов.

        Возвращает:
            UrlManager: Объект UrlManager, инициализированный данными из DataFrame.
        """
        manager = cls('')
        manager.df = df.copy()
        manager.file_path = file_path
        return manager