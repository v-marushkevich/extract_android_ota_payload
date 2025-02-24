from CTkMessagebox import CTkMessagebox
from ota_extractor import extract_ota


def start_progress(progressbar, lang, file_path, folder_path, log_message):
    """Запускает процесс распаковки OTA с обновлением прогресса
    Starts the OTA extraction process with progress updates"""

    def update_progress(value):
        progressbar.set(value)
        progressbar.update_idletasks()

    log_message(lang["log_extracting"].format(file=file_path, folder=folder_path))
    extract_ota(file_path, folder_path, update_progress, log_message, lang)
    log_message(lang["log_extraction_done"])

    # После завершения показываем сообщение / Show message after completion
    CTkMessagebox(
        title=lang["success_window"],
        message=lang["progress_done"],
        icon="check",
        option_1=lang["ok"],
    )
