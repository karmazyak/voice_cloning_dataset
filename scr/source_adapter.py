from scr.downloaders import rutube_downloader
from scr.downloaders.vk_parser.parsing_vk import download_audio_vk_video
from scr.downloaders.youtube_downloader import download_youtube


class SourceAdapter:
    '''
    Класс адаптер для вызова соответствующих загрузчиков
    
    Пример использования:
    urls = [
        'https://rutube.ru/video/77f41a478a208eacbe4d55956480cbd0/', 
    ]
    
    for url in urls:
        print(SourceAdapter.download(
            url, 'rutube', 'outputs', print_stats=True)
        )
    '''

    @staticmethod
    def download(url, source_type, download_dir,
                 rate=24000, print_stats=True, return_numpy=True):
        """
        Метод загрузки видео/аудио контента с различных платформ.

        Параметры:
        ----------
        url : str
            URL для загрузки контента.
        source_type : str
            Тип источника (например, 'rutube', 'youtube', 'vk').
        download_dir : str
            Директория для сохранения загруженных файлов.
        rate : int, optional
            Частота дискретизации аудио (по умолчанию 24000).
        print_stats : bool, optional
            Флаг для вывода информации процесса загрузки (по умолчанию True).
        return_numpy : bool, optional
            Возвращать ли аудио в формате NumPy в данных (по умолчанию True).

        Возвращает:
        -----------
        dict
            Словарь с данными и информацией о загруженном контенте.
        """
        if(source_type == 'rutube'):
            if type(url) == str:
                return(rutube_downloader.download_rutube(
                        url,
                        download_dir,
                        rate=rate,
                        print_stats=print_stats,
                        return_numpy=return_numpy))
        elif(source_type == 'youtube'):
            if type(url) == str:
                urls = [url]
                return download_youtube(urls, download_dir,
                                        target_sample_rate=rate)[0]
            elif type(url) == list:
                return download_youtube(url, download_dir,
                                        target_sample_rate=rate)
        elif(source_type == 'vk'):
            if type(url) == str:
                urls = [url]
                return download_audio_vk_video(urls=urls,
                                               download_dir=download_dir,
                                               target_sample_rate=rate,
                                               verbose=print_stats)[0]
            elif type(url) == list:
                return download_audio_vk_video(urls=url,
                                               download_dir=download_dir,
                                               target_sample_rate=rate,
                                               verbose=print_stats)
        else:
            raise ValueError

