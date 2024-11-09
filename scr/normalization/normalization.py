import pickle
import os
from pathlib import Path
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from text_normalizer import normalize_russian

def read_pickle(pickle_path: str):
    with open(pickle_path, 'rb') as handle:
        p = pickle.load(handle)
    return p

def dump_pickle(pickle_data: dict, pickle_path: str):
    with open(pickle_path, 'wb') as handle:
        pickle.dump(pickle_data, handle, protocol=pickle.HIGHEST_PROTOCOL)

def process_single_file(pickle_file, save_folder_path=None, change_inplace=False):
    """
    Обрабатывает один файл pickle и сохраняет результат.

    Аргументы:
        pickle_file (Path): Путь к файлу pickle.
        save_folder_path (Path, необязательно): Путь к папке для сохранения результата.
        change_inplace (bool): Если True, файл будет изменен на месте.
    """
    try:
        data = read_pickle(pickle_file)
        
        if 'text' not in data:
            print(f"Skipping {pickle_file.name}: 'text' key not found.")
            return False
        
        if 'normalized_text' in data:
            # Skip already processed files
            return False
        
        # Normalize the text
        transcribed_data = data['text']
        text_with_filtered_disfluencies = transcribed_data.replace("[*]", "").replace("  ", " ").strip()
        data['normalized_text'] = normalize_russian(text_with_filtered_disfluencies)

        # Save the updated dictionary
        if change_inplace:
            dump_pickle(data, pickle_file)
        else:
            if save_folder_path:
                new_file_path = os.path.join(save_folder_path, pickle_file.name)
                if os.path.isfile(new_file_path):
                    print(f"File: {new_file_path} is overwritten")
                dump_pickle(data, new_file_path)
                
        return True
    except Exception as e:
        print(f"Error processing {pickle_file.name}: {e}")
        return False


def process_pickle_files(pickle_folder, save_folder=None, change_inplace=False, max_workers=10):
    """
    Обрабатывает все файлы pickle в указанной папке и нормализует текст с использованием многопоточности.

    Аргументы:
        pickle_folder (str): Путь к папке, содержащей файлы pickle.
        save_folder (str, необязательно): Путь к папке, в которой будут сохранены обновленные файлы pickle.
        change_inplace (bool): Если True, файлы будут изменены на месте. Если False, изменения будут сохранены в папке `save_folder`.
        max_workers (int, необязательно): Максимальное количество потоков для обработки файлов.
    """
    pickle_folder_path = Path(pickle_folder)
    
    # Ensure save folder exists if not modifying in place
    if not change_inplace:
        if save_folder is None:
            raise ValueError("save_folder is None, but change_inplace set to False")
        save_folder_path = Path(save_folder)
        save_folder_path.mkdir(parents=True, exist_ok=True)
    else:
        save_folder_path = None

    # Get all pickle files
    pickle_files = list(pickle_folder_path.glob('*.pickle'))

    # Use ThreadPoolExecutor to process files in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(process_single_file, pickle_file, save_folder_path, change_inplace)
            for pickle_file in pickle_files
        ]

        # Wait for all threads to complete and handle results
        for future in tqdm(as_completed(futures), total=len(futures), desc="Processing pickle files"):
            try:
                result = future.result()
            except Exception as e:
                print(f"Error during file processing: {e}")