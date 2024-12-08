import pandas as pd
from flask import Flask, render_template, request

app = Flask(__name__git)

# Путь к вашему Excel файлу
file_path = r'C:\Users\kadir\Desktop\random_tables.xlsx'

# Загружаем данные из Excel
try:
    xls = pd.ExcelFile(file_path)
    tables = xls.sheet_names  # Получаем список доступных таблиц
except Exception as e:
    tables = []
    print(f"Ошибка при загрузке файла: {e}")

@app.route("/", methods=["GET", "POST"])
def index():
    selected_table = None
    selected_fabric = None
    sizes = []
    total_price = None
    error_message = None

    if request.method == "POST":
        # Получаем выбор таблицы, ткани и размеров
        selected_table = request.form.get("выбор_листа")
        selected_fabric = request.form.get("ткань")
        sizes_str = request.form.get("размеры")

        # Если таблица выбрана
        if selected_table:
            try:
                # Загружаем данные для выбранной таблицы
                df = pd.read_excel(xls, sheet_name=selected_table, header=0)
                df.set_index(df.columns[0], inplace=True)  # Устанавливаем первую колонку как индекс (ткань)
                df.columns = df.columns.astype(str).str.strip()  # Приводим имена колонок к строковому виду
            except Exception as e:
                return f"Ошибка при загрузке таблицы: {e}"

            # Если ткань выбрана
            if selected_fabric:
                if sizes_str:  # Если размеры введены
                    sizes = sizes_str.split()  # Разделяем введенные размеры

                    # Функция для расчёта стоимости
                    def calculate_price(fabric, sizes):
                        total_price = 0
                        invalid_sizes = []
                        for size in sizes:
                            size = str(size).strip()  # Преобразуем размер в строку и убираем пробелы
                            if size in df.columns:
                                try:
                                    price = float(df.at[fabric, size])  # Получаем цену для ткани и размера
                                    total_price += price
                                except ValueError:
                                    continue
                            else:
                                invalid_sizes.append(size)
                        return total_price, invalid_sizes

                    # Рассчитываем общую стоимость и получаем неправильные размеры
                    total_price, invalid_sizes = calculate_price(selected_fabric, sizes)

                    # Если есть неверные размеры, выводим ошибку
                    if invalid_sizes:
                        error_message = f"Некорректные размеры: {', '.join(invalid_sizes)}. Пожалуйста, введите правильные размеры."
                else:
                    error_message = "Пожалуйста, введите размеры."
            elif not selected_fabric:
                error_message = "Пожалуйста, выберите ткань."
        else:
            error_message = "Пожалуйста, выберите таблицу."

        return render_template(
            "index.html",
            tables=tables,
            selected_table=selected_table,
            selected_fabric=selected_fabric,
            sizes=sizes,
            total_price=total_price,
            error_message=error_message,
            df=df if selected_table else None
        )

    return render_template("index.html", tables=tables)

if __name__ == "__main__":
    app.run(debug=True)