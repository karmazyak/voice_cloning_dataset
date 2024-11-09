from scr.data_downloader import DataDownloader
import time
from scr.urlstore.url_manager import UrlManager
import argparse
import os

def get_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "--csv-path",
        type=str,
        help="Path to CSV file",
    )

    parser.add_argument(
        "--dataset-path",
        type=str,
        help="Path to dir where to create dataset",
    )

    parser.add_argument(
        "--logging-path",
        type=str,
        help="Path to logging file",
    )

    parser.add_argument(
        "--retry-sleep",
        type=float,
        default=3.0,
        help="Time of sleep between retries to download video (default: 3.0 seconds)",
    )

    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum number of retries to download video (default: 3)",
    )

    parser.add_argument(
        "--num-workers",
        type=int,
        default=2,
        help="Number of parallel workers (using threads, default: 2)",
    )

    return parser


def run_from_csv(csv_path, dataset_path, logging_path, retry_sleep=3, max_retries=3, num_workers=2):
    """
    Запускает загрузку WAV-файлов из CSV-файла с URL-адресами из источников.

    Параметры
    ----------
    csv_path : str
        Путь к CSV-файлу с URL-адресами.
    dataset_path : str
        Путь к папке, в которой будет создан (или уже существует) датасет.
    logging_path : str
        Путь к CSV-файлу, в который будут записываться логи.
    retry_sleep : float
        Время ожидания между попытками повторной загрузки видео.
    max_retries : int
        Максимальное количество попыток повторной загрузки видео.
    num_workers : int
        Количество параллельных потоков (работников).
    """
    manager = UrlManager(csv_path)
    df = manager.get_all_urls()
    dd = DataDownloader(dataset_path, logging_path,
                        retry_sleep=retry_sleep,
                        max_retries=max_retries,
                        num_workers=num_workers
    )
    print(df)
    dd.run(df['url'].to_list(), df['source'].to_list(), df['quality'].to_list())


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    run_from_csv(args.csv_path, args.dataset_path, args.logging_path, retry_sleep=args.retry_sleep, max_retries=args.max_retries, num_workers=args.num_workers)