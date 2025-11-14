# app.py
from flask import Flask, render_template, request, jsonify
import json
import random
import os

app = Flask(__name__)

# --- Загрузка данных ---
TEST_DATA_FILE = 'db_test_data.json'

def load_test_data():
    """Загружает вопросы и ответы из JSON файла."""
    if not os.path.exists(TEST_DATA_FILE):
        print(f"Файл {TEST_DATA_FILE} не найден!")
        return []
    try:
        with open(TEST_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError:
        print(f"Ошибка при чтении JSON из файла {TEST_DATA_FILE}")
        return []
    except Exception as e:
        print(f"Произошла ошибка при загрузке данных: {e}")
        return []

# --- Маршруты ---
@app.route('/')
def index():
    """Главная страница."""
    total_questions = len(load_test_data())
    return render_template('index.html', total_questions=total_questions)

@app.route('/start_test', methods=['POST'])
def start_test():
    """Начать тест."""
    data = request.get_json()
    num_questions = data.get('num_questions', 10)
    all_questions = load_test_data()

    if len(all_questions) == 0:
        return "Нет доступных вопросов для теста.", 500

    # Выбираем случайные вопросы
    selected_questions = random.sample(all_questions, min(num_questions, len(all_questions)))

    # Перемешиваем варианты ответов для каждого вопроса
    for q in selected_questions:
        options_with_index = list(enumerate(q['options']))
        random.shuffle(options_with_index)
        shuffled_options = [item[1] for item in options_with_index]
        # Новый индекс правильного ответа после перемешивания
        original_correct_index = q['correct_answer_index']
        new_correct_index = next(i for i, (idx, opt) in enumerate(options_with_index) if idx == original_correct_index)
        q['shuffled_options'] = shuffled_options
        q['new_correct_index'] = new_correct_index

    return render_template('test.html', questions=selected_questions, num_questions=len(selected_questions))

@app.route('/submit_test', methods=['POST'])
def submit_test():
    """Отправить тест и получить результат."""
    data = request.get_json()
    selected_questions = data.get('questions', [])
    user_answers = data.get('answers', [])
    num_questions = len(selected_questions)

    correct_count = 0
    detailed_results = []

    for i, q in enumerate(selected_questions):
        user_answer_index = user_answers[i] # Индекс выбранного пользователем варианта (в перемешанном списке)
        correct_answer_index = q['new_correct_index'] # Индекс правильного варианта (в перемешанном списке)
        is_correct = (user_answer_index == correct_answer_index)
        if is_correct:
            correct_count += 1

        detailed_results.append({
            'question': q['question'],
            'options': q['shuffled_options'],
            'correct_index': correct_answer_index,
            'user_index': user_answer_index,
            'is_correct': is_correct
        })

    score = (correct_count / num_questions) * 100 if num_questions > 0 else 0

    return jsonify({
        'score': score,
        'correct_count': correct_count,
        'total_count': num_questions,
        'detailed_results': detailed_results
    })

@app.route('/result')
def show_result():
    """Страница с результатами (временно, основная логика в /submit_test)."""
    # Эта страница будет отображаться после отправки теста через JavaScript
    # или может быть частью логики /submit_test, если мы будем рендерить её напрямую,
    # но это менее гибко для клиента. Оставим как отдельный маршрут, но используем JS.
    # Пока просто рендерим заглушку или используем JS.
    return render_template('result.html')

if __name__ == '__main__':
    app.run(debug=True)