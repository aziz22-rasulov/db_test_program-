# streamlit_app.py
import streamlit as st
import json
import random
import os

# --- Загрузка данных ---
TEST_DATA_FILE = 'db_test_data.json' # Убедитесь, что имя файла совпадает

@st.cache_data
def load_test_data():
    """Загружает вопросы и ответы из JSON файла. Кэшируется для оптимизации."""
    if not os.path.exists(TEST_DATA_FILE):
        st.error(f"Файл {TEST_DATA_FILE} не найден!")
        return []
    try:
        with open(TEST_DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Предполагаем, что JSON имеет структуру: [{"id": ..., "question": ..., "options": [...], "correct": ...}, ...]
        # или [{"question": ..., "options": [...], "correct": ...}, ...]
        # Проверим первый элемент
        if not data or 'question' not in data[0] or 'options' not in data[0] or 'correct' not in data[0]:
             st.error(f"Файл {TEST_DATA_FILE} имеет неправильный формат. Ожидается список словарей с ключами 'question', 'options', 'correct'.")
             return []
        return data
    except json.JSONDecodeError:
        st.error(f"Ошибка при чтении JSON из файла {TEST_DATA_FILE}")
        return []
    except Exception as e:
        st.error(f"Произошла ошибка при загрузке данных: {e}")
        return []

# --- Инициализация состояния сессии ---
if 'state' not in st.session_state:
    st.session_state.state = 'menu'  # Возможные состояния: 'menu', 'study', 'test', 'result'
    st.session_state.questions = []
    st.session_state.user_answers = []
    st.session_state.score = 0
    st.session_state.correct_count = 0
    st.session_state.total_count = 0
    st.session_state.detailed_results = []
    st.session_state.num_questions = 10 # Количество вопросов по умолчанию для экзамена
    st.session_state.current_question_index = 0 # Индекс текущего вопроса в режиме заучивания

# --- Загрузка данных ---
all_questions = load_test_data()
total_questions = len(all_questions)

if total_questions == 0:
    st.error("Нет доступных вопросов для теста.")
    st.stop() # Останавливаем выполнение, если нет вопросов

# --- Заголовок приложения ---
st.title("Тест по Базам Данных")

# --- Меню выбора режима ---
if st.session_state.state == 'menu':
    st.subheader("Выберите режим:")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Режим заучивания"):
            st.session_state.state = 'study'
            st.session_state.current_question_index = 0 # Сброс индекса при входе в режим заучивания
            st.rerun()
    with col2:
        if st.button("Мини-экзамен"):
            st.session_state.state = 'test_setup' # Переход к настройке экзамена
            st.rerun()

# --- Режим заучивания ---
elif st.session_state.state == 'study':
    st.subheader("Режим заучивания")
    st.write(f"Всего вопросов: {total_questions}")

    # Выбор конкретного вопроса
    selected_index = st.selectbox("Выберите номер вопроса:", options=range(1, total_questions + 1), index=st.session_state.current_question_index)
    st.session_state.current_question_index = selected_index - 1 # Обновляем индекс в состоянии

    # Отображение выбранного вопроса и ответа
    current_q = all_questions[st.session_state.current_question_index]
    st.markdown(f"**Вопрос {st.session_state.current_question_index + 1}:** {current_q['question']}")
    # Показываем *все* варианты, подсвечивая правильный
    st.write("**Варианты ответа:**")
    for i, opt in enumerate(current_q['options']):
        # Используем 'correct' для определения правильного ответа
        if i == current_q['correct']:
            st.write(f"**✅ Правильный ответ:** {opt}")
        else:
            st.write(f"❌ {opt}")

    # Кнопки навигации
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("Предыдущий", disabled=(st.session_state.current_question_index == 0)):
            st.session_state.current_question_index -= 1
            st.rerun()
    with col3:
        if st.button("Следующий", disabled=(st.session_state.current_question_index == total_questions - 1)):
            st.session_state.current_question_index += 1
            st.rerun()

    # Кнопка возврата в меню
    if st.button("Вернуться в меню"):
        st.session_state.state = 'menu'
        st.rerun()

# --- Настройка мини-экзамена ---
elif st.session_state.state == 'test_setup':
    st.subheader("Настройка мини-экзамена")
    st.write(f"Всего доступно вопросов: {total_questions}")

    # Используем session_state для хранения выбранного количества вопросов
    num_questions = st.number_input(
        "Выберите количество вопросов для экзамена:",
        min_value=1,
        max_value=total_questions,
        value=st.session_state.num_questions, # Используем значение из session_state
        step=1
    )
    # Сохраняем выбор в session_state
    st.session_state.num_questions = num_questions

    if st.button("Начать мини-экзамен"):
        # Выбираем случайные вопросы
        selected_questions = random.sample(all_questions, min(num_questions, total_questions))

        # Перемешиваем варианты ответов для каждого вопроса
        for q in selected_questions:
            options_with_index = list(enumerate(q['options']))
            random.shuffle(options_with_index)
            shuffled_options = [item[1] for item in options_with_index]
            # Новый индекс правильного ответа после перемешивания
            original_correct_index = q['correct'] # Используем 'correct' из исходного JSON
            new_correct_index = next(i for i, (idx, opt) in enumerate(options_with_index) if idx == original_correct_index)
            q['shuffled_options'] = shuffled_options
            q['new_correct_index'] = new_correct_index

        st.session_state.questions = selected_questions
        st.session_state.user_answers = [None] * len(selected_questions) # Инициализируем список ответов
        st.session_state.state = 'test'
        st.rerun() # Перезапускаем скрипт для отображения теста

    # Кнопка возврата в меню
    if st.button("Вернуться в меню"):
        st.session_state.state = 'menu'
        st.rerun()

# --- Режим мини-экзамена ---
elif st.session_state.state == 'test':
    # Страница прохождения теста
    questions = st.session_state.questions
    user_answers = st.session_state.user_answers

    st.subheader("Мини-экзамен")
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
    if st.button("Завершить экзамен"):
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

    # Кнопка возврата в меню
    if st.button("Вернуться в меню"):
        st.session_state.state = 'menu'
        st.session_state.questions = []
        st.session_state.user_answers = []
        st.session_state.score = 0
        st.session_state.correct_count = 0
        st.session_state.total_count = 0
        st.session_state.detailed_results = []
        st.rerun()

elif st.session_state.state == 'result':
    # Страница результатов
    st.header("Результаты мини-экзамена")
    st.metric("Правильных ответов", f"{st.session_state.correct_count} из {st.session_state.total_count}")
    st.metric("Процент", f"{st.session_state.score:.2f}%")

    st.subheader("Детализация:")
    for i, res in enumerate(st.session_state.detailed_results):
        st.markdown(f"**{i+1}. {res['question']}**")
        st.write(f"**Ваш ответ:** {'✅' if res['is_correct'] else '❌'} {res['user_text']}")
        if not res['is_correct']:
            st.write(f"**Правильный ответ:** {res['correct_text']}")
        st.markdown("---") # Разделитель между вопросами

    # Кнопка "Новый экзамен"
    if st.button("Пройти мини-экзамен снова"):
        # Сбрасываем состояние только для экзамена и результатов
        st.session_state.state = 'test_setup' # Возвращаемся к настройке экзамена
        st.session_state.questions = []
        st.session_state.user_answers = []
        st.session_state.score = 0
        st.session_state.correct_count = 0
        st.session_state.total_count = 0
        st.session_state.detailed_results = []
        # num_questions остается тем же, что и было выбрано последним
        st.rerun() # Перезапускаем скрипт

    # Кнопка "Вернуться в меню"
    if st.button("Вернуться в меню"):
        st.session_state.state = 'menu'
        st.rerun()
