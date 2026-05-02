import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary - Дневник погоды")
        self.root.geometry("900x650")
        self.root.resizable(True, True)
        
        # Настройка стилей
        self.root.configure(bg='#f0f0f0')
        
        self.entries = []  # Список записей
        self.filename = "weather_data.json"
        
        # Загрузка данных из файла при старте
        self.load_from_file(self.filename, silent=True)
        
        # Создание интерфейса
        self.create_widgets()
        self.update_table()
    
    def create_widgets(self):
        # Основной контейнер с прокруткой
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Рамка для ввода данных
        input_frame = ttk.LabelFrame(main_container, text="Добавление записи", padding=10)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Поля ввода
        # Дата
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.date_entry = ttk.Entry(input_frame, width=20)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Температура
        ttk.Label(input_frame, text="Температура (°C):").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.temp_entry = ttk.Entry(input_frame, width=15)
        self.temp_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Описание погоды
        ttk.Label(input_frame, text="Описание:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.desc_entry = ttk.Entry(input_frame, width=40)
        self.desc_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5)
        
        # Осадки (да/нет)
        self.precipitation_var = tk.BooleanVar()
        ttk.Checkbutton(input_frame, text="Осадки", variable=self.precipitation_var).grid(row=1, column=3, padx=5, pady=5)
        
        # Кнопка добавления
        ttk.Button(input_frame, text="➕ Добавить запись", command=self.add_entry).grid(row=2, column=0, columnspan=4, pady=10)
        
        # Рамка для фильтрации
        filter_frame = ttk.LabelFrame(main_container, text="Фильтрация записей", padding=10)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Фильтр по дате
        ttk.Label(filter_frame, text="Фильтр по дате (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=5, pady=5)
        self.filter_date_entry = ttk.Entry(filter_frame, width=20)
        self.filter_date_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Фильтр по температуре
        ttk.Label(filter_frame, text="Температура выше:").grid(row=0, column=2, padx=5, pady=5)
        self.filter_temp_entry = ttk.Entry(filter_frame, width=10)
        self.filter_temp_entry.grid(row=0, column=3, padx=5, pady=5)
        ttk.Label(filter_frame, text="°C").grid(row=0, column=4, padx=5, pady=5)
        
        # Кнопки фильтрации
        filter_buttons_frame = ttk.Frame(filter_frame)
        filter_buttons_frame.grid(row=1, column=0, columnspan=5, pady=10)
        
        ttk.Button(filter_buttons_frame, text="🔍 Применить фильтр", command=self.apply_filter).pack(side=tk.LEFT, padx=5)
        ttk.Button(filter_buttons_frame, text="🔄 Сбросить фильтр", command=self.reset_filter).pack(side=tk.LEFT, padx=5)
        
        # Рамка для таблицы записей
        table_frame = ttk.LabelFrame(main_container, text="Записи о погоде", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Таблица (Treeview)
        columns = ("Дата", "Температура", "Описание", "Осадки")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Настройка заголовков
        self.tree.heading("Дата", text="Дата")
        self.tree.heading("Температура", text="Температура (°C)")
        self.tree.heading("Описание", text="Описание")
        self.tree.heading("Осадки", text="Осадки")
        
        # Настройка ширины колонок
        self.tree.column("Дата", width=120)
        self.tree.column("Температура", width=120)
        self.tree.column("Описание", width=300)
        self.tree.column("Осадки", width=100)
        
        # Добавление скролла
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки управления файлами
        file_buttons_frame = ttk.Frame(main_container)
        file_buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(file_buttons_frame, text="💾 Сохранить в JSON", command=self.save_to_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_buttons_frame, text="📂 Загрузить из JSON", command=self.load_from_file_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_buttons_frame, text="🗑️ Удалить выбранную запись", command=self.delete_entry).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_buttons_frame, text="❌ Очистить все записи", command=self.clear_all_entries).pack(side=tk.LEFT, padx=5)
    
    def validate_date(self, date_str):
        """Проверка формата даты"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def add_entry(self):
        """Добавление новой записи"""
        date = self.date_entry.get().strip()
        temp = self.temp_entry.get().strip()
        description = self.desc_entry.get().strip()
        precipitation = self.precipitation_var.get()
        
        # Валидация данных
        if not date:
            messagebox.showerror("Ошибка", "Дата не может быть пустой!")
            return
        
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД")
            return
        
        try:
            temperature = float(temp)
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом!")
            return
        
        if not description:
            messagebox.showerror("Ошибка", "Описание погоды не может быть пустым!")
            return
        
        # Создание записи
        entry = {
            "date": date,
            "temperature": temperature,
            "description": description,
            "precipitation": "Да" if precipitation else "Нет"
        }
        
        self.entries.append(entry)
        self.update_table()
        
        # Очистка полей ввода
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.precipitation_var.set(False)
        
        messagebox.showinfo("Успех", "Запись успешно добавлена!")
    
    def update_table(self, entries_to_show=None):
        """Обновление таблицы"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Отображение записей
        data_to_show = entries_to_show if entries_to_show is not None else self.entries
        
        for entry in data_to_show:
            self.tree.insert("", tk.END, values=(
                entry["date"],
                entry["temperature"],
                entry["description"],
                entry["precipitation"]
            ))
    
    def apply_filter(self):
        """Применение фильтров"""
        filter_date = self.filter_date_entry.get().strip()
        filter_temp = self.filter_temp_entry.get().strip()
        
        filtered_entries = self.entries.copy()
        
        # Фильтр по дате
        if filter_date:
            if not self.validate_date(filter_date):
                messagebox.showerror("Ошибка", "Неверный формат даты фильтра!")
                return
            filtered_entries = [e for e in filtered_entries if e["date"] == filter_date]
        
        # Фильтр по температуре
        if filter_temp:
            try:
                temp_threshold = float(filter_temp)
                filtered_entries = [e for e in filtered_entries if e["temperature"] > temp_threshold]
            except ValueError:
                messagebox.showerror("Ошибка", "Температура фильтра должна быть числом!")
                return
        
        if not filtered_entries:
            messagebox.showinfo("Результат", "Записей, соответствующих фильтру, не найдено.")
        
        self.update_table(filtered_entries)
    
    def reset_filter(self):
        """Сброс фильтров"""
        self.filter_date_entry.delete(0, tk.END)
        self.filter_temp_entry.delete(0, tk.END)
        self.update_table()
    
    def delete_entry(self):
        """Удаление выбранной записи"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления!")
            return
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить выбранную запись?"):
            # Получение индекса выбранной записи
            index = self.tree.index(selected[0])
            del self.entries[index]
            self.update_table()
            messagebox.showinfo("Успех", "Запись удалена!")
    
    def clear_all_entries(self):
        """Очистка всех записей"""
        if not self.entries:
            messagebox.showinfo("Информация", "Нет записей для удаления.")
            return
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить ВСЕ записи?"):
            self.entries.clear()
            self.update_table()
            messagebox.showinfo("Успех", "Все записи удалены!")
    
    def save_to_file(self):
        """Сохранение записей в JSON файл"""
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.entries, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", f"Данные успешно сохранены в файл '{self.filename}'!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {str(e)}")
    
    def load_from_file(self, filename, silent=False):
        """Загрузка записей из JSON файла"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    self.entries = json.load(f)
                if not silent:
                    self.update_table()
                    messagebox.showinfo("Успех", f"Данные успешно загружены из файла '{filename}'!")
            elif not silent:
                messagebox.showwarning("Предупреждение", f"Файл '{filename}' не найден.")
        except Exception as e:
            if not silent:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {str(e)}")
    
    def load_from_file_dialog(self):
        """Загрузка из файла через диалоговое окно"""
        filename = filedialog.askopenfilename(
            title="Выберите JSON файл",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.load_from_file(filename)

def main():
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()

if __name__ == "__main__":
    main()
