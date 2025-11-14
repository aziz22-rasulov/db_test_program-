# streamlit_app.py
import streamlit as st
import json
import random
import os

# --- Загрузка данных ---
TEST_DATA_FILE = 'db_test_data.json'

@st.cache_data
def load_test_data():
    """Загружает вопросы и ответы из JSON файла. Кэшируется для оптимизации."""
    if not os.path.exists(TEST_DATA_FILE):
        st.error(f"Файл {TEST_DATA_FILE} не найден!")
        return []
    try:
        with open(TEST_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError:
        st.error(f"Ошибка при чтении JSON из файла {TEST_DATA_FILE}")
        return []
    except Exception as e:
        st.error(f"Произошла ошибка при загрузке данных: {e}")
        return []

# --- Инициализация состояния сессии ---
if 'state' not in st.session_state:
    st.session_state.state = 'start'  # Возможные состояния: 'start', 'test', 'result'
    st.session_state.questions = []
    st.session_state.user_answers = []
    st.session_state.score = 0
    st.session_state.correct_count = 0
    st.session_state.total_count = 0
    st.session_state.detailed_results = []

# --- Заголовок приложения ---
st.title("Тест по Базам Данных")

# --- Логика приложения в зависимости от состояния ---
if st.session_state.state == 'start':
    # Страница выбора количества вопросов
    all_questions = load_test_data()
    total_questions = len(all_questions)

    if total_questions == 0:
        st.error("Нет доступных вопросов для теста.")
    else:
        st.write(f"Всего доступно вопросов: {total_questions}")
        num_questions = st.number_input("Выберите количество вопросов для теста:", min_value=1, max_value=total_questions, value=10, step=1)

        if st.button("Начать тест"):
            # Выбираем случайные вопросы
            selected_questions = random.sample(all_questions, min(num_questions, total_questions))

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

            st.session_state.questions = selected_questions
            st.session_state.user_answers = [None] * len(selected_questions) # Инициализируем список ответов
            st.session_state.state = 'test'
            st.rerun() # Перезапускаем скрипт для отображения теста

elif st.session_state.state == 'test':
    # Страница прохождения теста
    questions = st.session_state.questions
    user_answers = st.session_state.user_answers

    st.write(f"Вопросы: {len(questions)}")

    # Отображаем каждый вопрос и варианты ответов
    for i, q in enumerate(questions):
        st.subheader(f"Вопрос {i+1}: {q['question']}")
        options = q['shuffled_options']
        # Используем selectbox, чтобы гарантировать один выбранный вариант
        selected_option = st.radio(
            label="Выберите ответ:",
            options=options,
            key=f"question_{i}", # Уникальный ключ для каждого вопроса
            index=options.index(user_answers[i]) if user_answers[i] is not None else 0 # Восстанавливаем предыдущий выбор
        )
        # Сохраняем выбранный вариант в списке ответов
        user_answers[i] = selected_option

    # Кнопка отправки теста
    if st.button("Завершить тест"):
        correct_count = 0
        detailed_results = []

        for i, q in enumerate(questions):
            selected_answer = user_answers[i]
            correct_answer_index = q['new_correct_index']
            correct_answer_text = q['shuffled_options'][correct_answer_index]

            is_correct = (selected_answer == correct_answer_text)
            if is_correct:
                correct_count += 1

            detailed_results.append({
                'question': q['question'],
                'options': q['shuffled_options'],
                'correct_index': correct_answer_index,
                'correct_text': correct_answer_text,
                'user_text': selected_answer,
                'is_correct': is_correct
            })

        total_count = len(questions)
        score = (correct_count / total_count) * 100 if total_count > 0 else 0

        st.session_state.score = score
        st.session_state.correct_count = correct_count
        st.session_state.total_count = total_count
        st.session_state.detailed_results = detailed_results
        st.session_state.state = 'result'
        st.rerun() # Перезапускаем скрипт для отображения результатов

elif st.session_state.state == 'result':
    # Страница результатов
    st.header("Результаты теста")
    st.metric("Правильных ответов", f"{st.session_state.correct_count} из {st.session_state.total_count}")
    st.metric("Процент", f"{st.session_state.score:.2f}%")

    st.subheader("Детализация:")
    for i, res in enumerate(st.session_state.detailed_results):
        st.markdown(f"**{i+1}. {res['question']}**")
        st.write(f"**Ваш ответ:** {'✅' if res['is_correct'] else '❌'} {res['user_text']}")
        if not res['is_correct']:
            st.write(f"**Правильный ответ:** {res['correct_text']}")
        st.markdown("---") # Разделитель между вопросами

    # Кнопка "Новый тест"
    if st.button("Пройти тест снова"):
        # Сбрасываем состояние
        st.session_state.state = 'start'
        st.session_state.questions = []
        st.session_state.user_answers = []
        st.session_state.score = 0
        st.session_state.correct_count = 0
        st.session_state.total_count = 0
        st.session_state.detailed_results = []
        st.rerun() # Перезапускаем скрипт для возврата на старт
