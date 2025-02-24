from customtkinter import filedialog


def select_file(lang):
    """Открывает диалог выбора файла с фильтрацией по типам"""
    return filedialog.askopenfilename(
        title=lang["select_file"],
        filetypes=[
            ("Binary files", "*.bin"),
            ("ZIP archives", "*.zip"),
            ("All Files", "*.*"),
        ],
    )


def select_folder(lang):
    """Открывает диалог выбора папки"""
    return filedialog.askdirectory(title=lang["select_folder"])
