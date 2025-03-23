import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeView, QVBoxLayout, QWidget, QMenu, QFileDialog, QComboBox, QInputDialog
from PyQt6.QtGui import QFileSystemModel, QAction
from PyQt6.QtCore import QDir, Qt, QFile

class FileManager(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Файловый менеджер")
        self.setGeometry(100, 100, 800, 600)

        # Главный виджет и макет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        self.disk_selector = QComboBox()
        self.disk_selector.addItems(self.get_available_drives())
        self.disk_selector.currentIndexChanged.connect(self.change_disk)
        layout.addWidget(self.disk_selector)

        # Создаём модель файловой системы
        self.model = QFileSystemModel()
        self.model.setRootPath("")  # Указываем корневую папку

        # Создаём дерево файловой системы
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index("C:/"))  # Укажи свою папку

        if self.disk_selector.count() > 0:
            self.change_disk(0)

        # Добавляем в макет
        layout.addWidget(self.tree)

        # Подключаем контекстное меню
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)

    def get_available_drives(self):
        drives = [drive.path() for drive in QDir.drives()]
        return drives if drives else ["C:/"]
    
    def change_disk(self, index):
        selected_drive = self.disk_selector.itemText(index)
        self.tree.setRootIndex(self.model.setRootPath(selected_drive))

    def show_context_menu(self, position):
        # Получаем индекс элемента в дереве
        index = self.tree.indexAt(position)
        menu = QMenu()
        if index.isValid():
            menu = QMenu()

            # Добавляем действия в меню
            delete_action = QAction("Удалить", self)
            delete_action.triggered.connect(lambda: self.delete_file(index))
            menu.addAction(delete_action)

            rename_action = QAction("Переименовать", self)
            rename_action.triggered.connect(lambda: self.rename_file(index))
            menu.addAction(rename_action)

            move_action = QAction("Переместить", self)
            move_action.triggered.connect(lambda: self.move_file(index))
            menu.addAction(move_action)

            copy_action = QAction("Копировать", self)
            copy_action.triggered.connect(lambda: self.copy_file(index))
            menu.addAction(copy_action)

        create_folder_action = QAction("Создать папку", self)
        create_folder_action.triggered.connect(lambda: self.create_folder(index))
        menu.addAction(create_folder_action)

        create_file_action = QAction("Создать текстовый файл", self)
        create_file_action.triggered.connect(lambda: self.create_text_file(index))
        menu.addAction(create_file_action)

        menu.exec(self.tree.viewport().mapToGlobal(position))

    def create_folder(self, index):
        path = self.model.filePath(index) if index.isValid() else self.model.rootPath()
        name, ok = QInputDialog.getText(self, "Создать папку", "Введите имя папки:")
        if ok and name:
            folder_path = f"{path}/{name}"
            if not QDir(folder_path).exists():
                QDir().mkdir(folder_path)
                print(f"Папка создана: {folder_path}")
            else:
                print("Ошибка: такая папка уже существует")

    def create_text_file(self, index):
        path = self.model.filePath(index) if index.isValid() else self.model.rootPath()
        name, ok = QInputDialog.getText(self, "Создать файл", "Введите имя файла (без .txt):")
        if ok and name:
            file_path = f"{path}/{name}.txt"
            if not QFile(file_path).exists():
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write("")
                print(f"Файл создан: {file_path}")
            else:
                print("Ошибка: файл уже существует")

    def delete_file(self, index):
        # Получаем путь к файлу или папке
        path = self.model.filePath(index)

        # Печатаем путь для отладки
        print(f"Путь к файлу/папке: {path}")

        # Удаляем файл или папку
        if QFile(path).exists():
            if QFile(path).remove():  # Если это файл, удаляем
                print(f"Файл {path} удалён")
            else:
                print(f"Не удалось удалить файл {path}")
        elif QDir(path).exists():
            if QDir(path).removeRecursively():  # Если это папка, удаляем рекурсивно
                print(f"Папка {path} удалена")
            else:
                print(f"Не удалось удалить папку {path}")
        else:
            print("Ошибка: файл или папка не найдены")

    def rename_file(self, index):
        # Переименование файла
        path = self.model.filePath(index)
        new_name, _ = QFileDialog.getSaveFileName(self, "Выберите новое имя", path)

        if new_name and new_name != path:
            if QFile(path).rename(new_name):
                print(f"Файл переименован в {new_name}")
            else:
                print(f"Ошибка при переименовании {path}")
        else:
            print("Переименование отменено или имя не изменилось")

    def move_file(self, index):
        source_path = self.model.filePath(index)
        destination_path = QFileDialog.getExistingDirectory(self, "Выберите папку для перемещения", source_path)

        if destination_path:
            dest_path = f"{destination_path}/{source_path.split('/')[-1]}"

            if QFile(source_path).rename(dest_path):
                print(f"Файл перемещён в {dest_path}")
            elif QDir(source_path).rename(source_path, dest_path):
                print(f"Папка перемещена в {dest_path}")
            else:
                print(f"Не удалось переместить {source_path}")
        else:
            print("Перемещение отменено")

    def copy_file(self, index):
        source_path = self.model.filePath(index)
        destination_path = QFileDialog.getExistingDirectory(self, "Выберите папку для копирования", source_path)

        if destination_path:
            dest_path = f"{destination_path}/{source_path.split('/')[-1]}"

            if QFile(source_path).copy(dest_path):
                print(f"Файл скопирован в {dest_path}")
            elif QDir(source_path).copy(source_path, dest_path):
                print(f"Папка скопирована в {dest_path}")
            else:
                print(f"Не удалось скопировать в {source_path}")
        else:
            print("Копирование отменено")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileManager()
    window.show()
    sys.exit(app.exec())
