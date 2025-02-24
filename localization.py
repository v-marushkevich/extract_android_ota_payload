import locale

translations = {
    "en": {
        "select_file": "Select File",
        "select_folder": "Select Folder",
        "start": "Start",
        "file_placeholder": "Select a file path...",
        "folder_placeholder": "Select a folder path...",
        "progress_done": "Unpacking completed successfully!",
        "ok": "OK",
        "success_window": "Process completed",
        "log_initialized": "Log initialized...",
        "log_selected_file": "Selected file: {file}",
        "log_selected_folder": "Selected folder: {folder}",
        "log_start_extraction": "Starting extraction...",
        "log_extracting": "Extracting {file} to {folder}...",
        "log_extraction_done": "Extraction completed successfully!",
        "log_creating_output_dir": "Creating output directory: {dir}",
        "log_opening_payload": "Opening payload file...",
        "log_processing_partition": "Processing partition: {partition}",
        "log_extraction_failed": "Extraction failed: {error}",
    },
    "ru": {
        "select_file": "Выбрать файл",
        "select_folder": "Выбрать папку",
        "start": "Запуск",
        "file_placeholder": "Выберите путь к файлу...",
        "folder_placeholder": "Выберите путь к папке...",
        "progress_done": "Распаковка успешно завершена!",
        "ok": "ОК",
        "success_window": "Процесс завершён",
        "log_initialized": "Лог инициализирован...",
        "log_selected_file": "Выбран файл: {file}",
        "log_selected_folder": "Выбрана папка: {folder}",
        "log_start_extraction": "Начало извлечения...",
        "log_extracting": "Извлечение {file} в {folder}...",
        "log_extraction_done": "Распаковка успешно завершена!",
        "log_creating_output_dir": "Создание выходной директории: {dir}",
        "log_opening_payload": "Открытие файла payload...",
        "log_processing_partition": "Обработка раздела: {partition}",
        "log_extraction_failed": "Ошибка извлечения: {error}",
    },
}


def get_language():
    system_lang = locale.getdefaultlocale()[0]
    return translations["ru"] if system_lang.startswith("ru") else translations["en"]
