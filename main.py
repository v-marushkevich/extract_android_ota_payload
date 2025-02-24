import customtkinter
from ui import MainUI
from localization import get_language


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("600x600")
        self.title("OTA Extractor")
        self._set_appearance_mode("system")

        # Определяем язык системы / Determine system language
        self.lang = get_language()

        # Загружаем UI / Load UI
        self.ui = MainUI(self, self.lang)
        self.ui.pack(expand=True, fill="both")


# Запуск приложения / Start the application
if __name__ == "__main__":
    app = App()
    app.mainloop()
