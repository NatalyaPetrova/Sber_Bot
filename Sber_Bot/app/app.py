from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employees.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Определение модели сотрудника
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    skill_level = db.Column(db.String(50), nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    availability = db.Column(db.String(50), nullable=False)


# Словарь для хранения предпочтений сотрудников
preferences_dict = {}


# Главная страница
@app.route('/')
def index():
    employees = Employee.query.all()
    return render_template('index.html', employees=employees)


# Добавление нового сотрудника
@app.route('/add_employee', methods=['POST'])
def add_employee():
    name = request.form['name']
    skill_level = request.form['skill_level']
    experience = int(request.form['experience'])  # Преобразуем в число
    availability = request.form['availability']

    new_employee = Employee(name=name, skill_level=skill_level,
                            experience=experience, availability=availability)

    db.session.add(new_employee)
    db.session.commit()

    return redirect(url_for('index'))


# Добавление предпочтений сотрудника
@app.route('/submit_preferences', methods=['POST'])
def submit_preferences():
    employee_id = int(request.form['employee_id'])
    preferences = request.form['preferences']

    # Сохранение предпочтений в словаре
    preferences_dict[employee_id] = preferences
    return redirect(url_for('index'))


# Страница редактирования предпочтений
@app.route('/edit_preferences/<int:employee_id>')
def edit_preferences(employee_id):
    employee = Employee.query.get(employee_id)
    return render_template('edit_preferences.html', employee=employee)


# Отображение предпочтений сотрудников
@app.route('/show_preferences')
def show_preferences():
    # Получаем все сотрудники
    employees = Employee.query.all()
    # Создаем словарь с предпочтениями и именами сотрудников
    preferences_with_names = {
        employee.id: {'name': employee.name, 'preferences': preferences_dict.get(employee.id, '')}
        for employee in employees
    }
    return render_template('preferences.html', preferences=preferences_with_names)


# Генерация расписания
# @app.route('/generate_schedule')
# def generate_schedule():
#     # Здесь должна быть логика генерации расписания
#     schedule = []  # Заглушка
#     return render_template('schedule.html', schedule=schedule)

@app.route('/generate_schedule')
def generate_schedule():
    employees = Employee.query.all()

    if not employees:
        return "Нет сотрудников для генерации расписания!", 400

    schedule = []
    total_priority = 0

    for e in employees:
        try:
            skill_level = float(e.skill_level)  # Разрешаем использовать десятичные значения (например, 2.5)
            experience = int(e.experience)  # Опыт в годах все равно должен быть целым
            availability_hours = int(''.join(filter(str.isdigit, e.availability)))  # Достаем число из строки
        except ValueError:
            return f"Ошибка в данных сотрудника {e.name}. Проверьте ввод!", 400

        priority = experience * skill_level
        total_priority += priority

        schedule.append({
            'name': e.name,
            'skill_level': skill_level,
            'experience': experience,
            'availability': availability_hours,
            'priority': priority
        })

    if total_priority == 0:
        return "Ошибка: у всех сотрудников нулевые приоритеты!", 400

    # Шаг 2: Распределение рабочих часов на основе приоритета
    for entry in schedule:
        entry['assigned_hours'] = round((entry['availability'] * entry['priority']) / total_priority, 1)

    return render_template('schedule.html', schedule=schedule)



@app.route('/edit_employee/<int:employee_id>', methods=['GET', 'POST'])
def edit_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)

    if request.method == 'POST':
        # Получаем данные из формы
        employee.name = request.form['name']
        employee.skill_level = float(request.form['skill_level'])  # Разрешаем дробные значения
        employee.experience = int(request.form['experience'])
        employee.availability = request.form['availability']

        db.session.commit()  # Сохраняем изменения

        return redirect(url_for('index'))

    return render_template('edit_employee.html', employee=employee)


@app.route('/delete_employee/<int:employee_id>', methods=['POST'])
def delete_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)  # Ищем сотрудника или выдаем ошибку 404

    db.session.delete(employee)  # Удаляем сотрудника из базы
    db.session.commit()  # Применяем изменения

    return redirect(url_for('index'))  # Перенаправляем на главную страницу


# Создание базы данных перед запуском сервера
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
