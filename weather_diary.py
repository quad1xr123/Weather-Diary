import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary - Дневник погоды")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        self.records = []  # Список для хранения записей
        self.load_data()   # Загружаем данные из JSON при старте
        
        # Создаем интерфейс
        self.create_input_frame()
        self.create_table_frame()
        self.create_filter_frame()
        
        # Обновляем таблицу
        self.refresh_table()
    
    def create_input_frame(self):
        """Фрейм для ввода новой записи"""
        input_frame = tk.LabelFrame(self.root, text="Добавить новую запись", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Дата
        tk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.date_entry = tk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Температура
        tk.Label(input_frame, text="Температура (°C):").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.temp_entry = tk.Entry(input_frame, width=10)
        self.temp_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Описание
        tk.Label(input_frame, text="Описание:").grid(row=0, column=4, sticky="w", padx=5, pady=5)
        self.desc_entry = tk.Entry(input_frame, width=20)
        self.desc_entry.grid(row=0, column=5, padx=5, pady=5)
        
        # Осадки (Checkbox)
        self.precip_var = tk.BooleanVar()
        tk.Checkbutton(input_frame, text="Осадки", variable=self.precip_var).grid(row=0, column=6, padx=10, pady=5)
        
        # Кнопка добавления
        tk.Button(input_frame, text="➕ Добавить запись", command=self.add_record, bg="lightgreen").grid(row=0, column=7, padx=10, pady=5)
    
    def create_table_frame(self):
        """Фрейм с таблицей записей"""
        table_frame = tk.LabelFrame(self.root, text="Список записей", padx=10, pady=10)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Создаем Treeview (таблицу)
        columns = ("date", "temperature", "description", "precipitation")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Настройка колонок
        self.tree.heading("date", text="Дата")
        self.tree.heading("temperature", text="Температура (°C)")
        self.tree.heading("description", text="Описание")
        self.tree.heading("precipitation", text="Осадки")
        
        self.tree.column("date", width=120)
        self.tree.column("temperature", width=100)
        self.tree.column("description", width=300)
        self.tree.column("precipitation", width=80)
        
        # Добавляем scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_filter_frame(self):
        """Фрейм для фильтрации"""
        filter_frame = tk.LabelFrame(self.root, text="Фильтрация записей", padx=10, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        # Фильтр по дате
        tk.Label(filter_frame, text="Фильтр по дате (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.filter_date_entry = tk.Entry(filter_frame, width=15)
        self.filter_date_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Button(filter_frame, text="Фильтровать по дате", command=self.filter_by_date).grid(row=0, column=2, padx=5, pady=5)
        tk.Button(filter_frame, text="Сбросить фильтр даты", command=self.reset_date_filter).grid(row=0, column=3, padx=5, pady=5)
        
        # Фильтр по температуре
        tk.Label(filter_frame, text="Температура выше (°C):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.filter_temp_entry = tk.Entry(filter_frame, width=10)
        self.filter_temp_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Button(filter_frame, text="Фильтровать по темп.", command=self.filter_by_temperature).grid(row=1, column=2, padx=5, pady=5)
        tk.Button(filter_frame, text="Сбросить фильтр темп.", command=self.reset_temp_filter).grid(row=1, column=3, padx=5, pady=5)
        
        # Кнопки сохранения/загрузки
        button_frame = tk.Frame(filter_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=10)
        
        tk.Button(button_frame, text="💾 Сохранить в JSON", command=self.save_to_json, bg="lightblue").pack(side="left", padx=5)
        tk.Button(button_frame, text="📂 Загрузить из JSON", command=self.load_from_json, bg="lightyellow").pack(side="left", padx=5)
        tk.Button(button_frame, text="🔄 Показать все записи", command=self.show_all_records, bg="lightgray").pack(side="left", padx=5)
        
        # Текущий фильтр
        self.filter_var = tk.StringVar()
        self.filter_var.set("Фильтр: нет")
        tk.Label(filter_frame, textvariable=self.filter_var, fg="blue").grid(row=3, column=0, columnspan=4, pady=5)
    
    def add_record(self):
        """Добавление новой записи с проверкой ввода"""
        date = self.date_entry.get().strip()
        temp = self.temp_entry.get().strip()
        description = self.desc_entry.get().strip()
        precipitation = "Да" if self.precip_var.get() else "Нет"
        
        # Проверка даты
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД")
            return
        
        # Проверка температуры
        try:
            temp_float = float(temp)
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом!")
            return
        
        # Проверка описания
        if not description:
            messagebox.showerror("Ошибка", "Описание не может быть пустым!")
            return
        
        # Добавляем запись
        record = {
            "date": date,
            "temperature": temp_float,
            "description": description,
            "precipitation": precipitation
        }
        self.records.append(record)
        
        # Очищаем поля
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.precip_var.set(False)
        
        # Автоматически сохраняем в JSON
        self.save_to_json()
        
        # Обновляем таблицу без фильтров
        self.show_all_records()
        
        messagebox.showinfo("Успех", "Запись добавлена!")
    
    def refresh_table(self, records_to_show=None):
        """Обновление таблицы"""
        # Очищаем таблицу
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        # Если не передан список для отображения, показываем все записи
        if records_to_show is None:
            records_to_show = self.records
        
        # Добавляем записи в таблицу
        for record in records_to_show:
            self.tree.insert("", "end", values=(
                record["date"],
                record["temperature"],
                record["description"],
                record["precipitation"]
            ))
    
    def filter_by_date(self):
        """Фильтрация по дате"""
        filter_date = self.filter_date_entry.get().strip()
        if not filter_date:
            messagebox.showwarning("Предупреждение", "Введите дату для фильтрации")
            return
        
        # Проверка формата даты
        try:
            datetime.strptime(filter_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД")
            return
        
        filtered = [r for r in self.records if r["date"] == filter_date]
        self.refresh_table(filtered)
        self.filter_var.set(f"Фильтр: дата = {filter_date} (найдено {len(filtered)} записей)")
    
    def filter_by_temperature(self):
        """Фильтрация по температуре (выше указанного значения)"""
        temp_str = self.filter_temp_entry.get().strip()
        if not temp_str:
            messagebox.showwarning("Предупреждение", "Введите значение температуры")
            return
        
        try:
            temp_threshold = float(temp_str)
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом!")
            return
        
        filtered = [r for r in self.records if r["temperature"] > temp_threshold]
        self.refresh_table(filtered)
        self.filter_var.set(f"Фильтр: температура > {temp_threshold}°C (найдено {len(filtered)} записей)")
    
    def reset_date_filter(self):
        """Сброс фильтра по дате"""
        self.filter_date_entry.delete(0, tk.END)
        self.show_all_records()
    
    def reset_temp_filter(self):
        """Сброс фильтра по температуре"""
        self.filter_temp_entry.delete(0, tk.END)
        self.show_all_records()
    
    def show_all_records(self):
        """Показать все записи"""
        self.refresh_table()
        self.filter_var.set("Фильтр: нет (все записи)")
    
    def save_to_json(self, filename=None):
        """Сохранение записей в JSON файл"""
        if filename is None:
            filename = "weather_diary.json"
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.records, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")
            return False
    
    def load_from_json(self):
        """Загрузка записей из JSON файла"""
        filename = filedialog.askopenfilename(
            title="Выберите JSON файл",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            with open(filename, "r", encoding="utf-8") as f:
                self.records = json.load(f)
            self.show_all_records()
            messagebox.showinfo("Успех", f"Загружено {len(self.records)} записей из {filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {e}")
    
    def load_data(self):
        """Автоматическая загрузка данных при старте"""
        if os.path.exists("weather_diary.json"):
            try:
                with open("weather_diary.json", "r", encoding="utf-8") as f:
                    self.records = json.load(f)
            except:
                self.records = []

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()