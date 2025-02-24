import tkinter

import customtkinter
from file_manager import select_file, select_folder
from progress_handler import start_progress


class MainUI(customtkinter.CTkFrame):
    def __init__(self, parent, lang):
        super().__init__(parent)
        self.lang = lang

        # Локализация / Localization
        texts = lang

        # Настройка сетки / Configure grid
        self.columnconfigure(1, weight=1)

        # Выбор файла / File selection
        self.button_select_file = customtkinter.CTkButton(
            self, text=texts["select_file"], command=self.select_file, width=120
        )
        self.entry_file_path = customtkinter.CTkEntry(
            self, placeholder_text=texts["file_placeholder"], width=350
        )

        # Выбор папки / Folder selection
        self.button_select_folder = customtkinter.CTkButton(
            self, text=texts["select_folder"], command=self.select_folder, width=120
        )
        self.entry_folder_path = customtkinter.CTkEntry(
            self, placeholder_text=texts["folder_placeholder"], width=350
        )

        # Прогрессбар / Progress bar
        self.button_start_progress = customtkinter.CTkButton(
            self,
            text=texts["start"],
            command=self.start_progress,
            width=120,
            state="disabled",
        )
        self.progressbar = customtkinter.CTkProgressBar(
            self, orientation="horizontal", mode="determinate", width=350
        )
        self.progressbar.set(0)

        # Окно логов / Log window
        self.text_log = customtkinter.CTkTextbox(
            self, height=430, width=480, wrap="word"
        )
        self.text_log.insert("end", texts["log_initialized"] + "\n")
        self.text_log.configure(state="disabled")

        # Размещение элементов / Layout elements
        self.button_select_file.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.entry_file_path.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.button_select_folder.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.entry_folder_path.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        self.button_start_progress.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.progressbar.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        self.text_log.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

    def select_file(self):
        file_path = select_file(self.lang)
        if file_path:
            self.entry_file_path.delete(0, "end")
            self.entry_file_path.insert(0, file_path)
            self.log_message(self.lang["log_selected_file"].format(file=file_path))
            self.update_start_button()

    def select_folder(self):
        folder_path = select_folder(self.lang)
        if folder_path:
            self.entry_folder_path.delete(0, "end")
            self.entry_folder_path.insert(0, folder_path)
            self.log_message(
                self.lang["log_selected_folder"].format(folder=folder_path)
            )
            self.update_start_button()

    def start_progress(self):
        file_path = self.entry_file_path.get()
        folder_path = self.entry_folder_path.get()
        if file_path and folder_path:
            self.log_message(self.lang["log_start_extraction"])
            self.button_start_progress.configure(state="disabled")
            start_progress(
                self.progressbar, self.lang, file_path, folder_path, self.log_message
            )
            self.button_start_progress.configure(state="normal")

    def log_message(self, message):
        """Добавляет сообщение в лог / Adds message to log"""
        self.text_log.configure(state="normal")
        self.text_log.insert("end", message + "\n")
        self.text_log.configure(state="disabled")
        self.text_log.yview("end")

    def update_start_button(self):
        """Разблокирует кнопку, если оба поля заполнены / Unlocks button if both fields are filled"""
        if self.entry_file_path.get() and self.entry_folder_path.get():
            self.button_start_progress.configure(state="normal")
        else:
            self.button_start_progress.configure(state="disabled")
