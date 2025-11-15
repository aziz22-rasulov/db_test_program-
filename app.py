import streamlit as st
import json
import random
import time


# ===================== ЗАГРУЗКА ДАННЫХ =====================
@st.cache_data
def load_data():
    # Используем имя файла, соответствующее вашему новому JSON
    with open("db_test_data.json", "r", encoding="utf-8") as f:
        # Если JSON не обёрнут в {"cards": [...]}, загружаем напрямую
        data = json.load(f)
        # Предполагаем, что data - это список словарей
        if isinstance(data, list) and len(data) > 0 and 'question' in data[0]:
            return data
        # Если JSON обёрнут в {"cards": [...]}, как в примере из файла Pasted_Text_1763202972036.txt
        elif isinstance(data, dict) and 'cards' in data:
            return data['cards']
        else:
            st.error("Неправильный формат JSON файла. Ожидается список вопросов или {'cards': [...]}.")
            return []

cards = load_data()

if not cards:
    st.error("Нет доступных вопросов для теста.")
    st.stop()


# ===================== НАСТРОЙКИ =====================
st.set_page_config(
    page_title="Тест по базам данных",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.sidebar.title("Навигация")
mode = st.sidebar.radio("Выберите режим:", ["Учебник", "Экзамен"])


# ======================================================================
#                              РЕЖИМ 1 — УЧЕБНИК
# ======================================================================
if mode == "Учебник":
    st.title("📘 Учебный режим")

    # Список вопросов
    question_numbers = [f"Вопрос {c['id']}" for c in cards]
    selected = st.selectbox("Выберите вопрос:", range(len(cards)),
                            format_func=lambda x: question_numbers[x])

    q = cards[selected]

    st.write(f"### {q['id']}. {q['question']}")

    st.write("#### Варианты ответа:")
    for opt in q["options"]:
        st.write("- " + opt)

    st.success("Правильный ответ:")
    st.write(q["options"][q["correct"]])

    # Объяснение можно добавить, если оно есть в JSON, например, как отдельное поле
    # st.info("Объяснение:")
    # st.write(q.get("explanation", "Объяснение отсутствует."))

    st.write("---")
    st.caption("Используйте меню слева, чтобы перейти в режим экзамена.")


# ======================================================================
#                       РЕЖИМ 2 — ЭКЗАМЕН
# ======================================================================
else:
    st.title("📝 Экзамен по базам данных")

    # ---------- Инициализация состояния ----------
    if "exam_started" not in st.session_state:
        st.session_state.exam_started = False
        st.session_state.current = 0
        st.session_state.score = 0
        st.session_state.answers = {}
        st.session_state.start_time = None
        st.session_state.time_per_question = {}
        st.session_state.order = []

    # ---------- Старт экзамена ----------
    if not st.session_state.exam_started:
        st.write("Нажмите кнопку ниже, чтобы начать экзамен.")
        if st.button("Начать экзамен"):
            st.session_state.exam_started = True
            st.session_state.current = 0
            st.session_state.score = 0
            st.session_state.answers = {}
            st.session_state.time_per_question = {}
            st.session_state.start_time = time.time()
            # Перемешиваем индексы вопросов из cards
            st.session_state.order = list(range(len(cards)))
            random.shuffle(st.session_state.order)
            # st.rerun() предпочтительнее для новых версий Streamlit
            st.rerun()
        st.stop()

    # ---------- Завершение экзамена ----------
    if st.session_state.current >= len(cards):
        total_time = int(time.time() - st.session_state.start_time)
        st.header("🎉 Экзамен завершён")

        st.subheader(f"Ваш результат: **{st.session_state.score} / {len(cards)}**")
        st.write(f"⏱ Общее время: {total_time} сек.")
        st.write("---")
        st.write("## 📘 Подробный отчёт")

        for i, user_answer in st.session_state.answers.items():
            # Используем перемешанный индекс, чтобы получить правильный вопрос
            q_original_index = st.session_state.order[i]
            q = cards[q_original_index]

            st.write(f"### Вопрос {q['id']}: {q['question']}")
            st.write(f"Ваш ответ: {q['options'][user_answer]}")
            st.write(f"Правильный: {q['options'][q['correct']]}")
            # Время для *этого* вопроса (по индексу в экзамене i) - может не совпадать с q_original_index
            # Нужно использовать i для доступа к времени, так как оно сохранялось по порядку ответов
            st.write(f"⏱ Время на вопрос: {st.session_state.time_per_question.get(i, 0)} сек")
            st.write("---")

        if st.button("Пройти снова"):
            # Сбрасываем только состояние экзамена
            keys_to_clear = ["exam_started", "current", "score", "answers", "start_time", "time_per_question", "order"]
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            # st.rerun() предпочтительнее для новых версий Streamlit
            st.rerun()

        st.stop()

    # ---------- Текущий вопрос ----------
    # Получаем индекс вопроса из перемешанного списка
    q_index_in_cards = st.session_state.order[st.session_state.current]
    question = cards[q_index_in_cards]

    st.write(f"Вопрос {st.session_state.current + 1} из {len(cards)}")

    # Прогресс
    st.progress((st.session_state.current + 1) / len(cards))

    # Таймер
    question_start = time.time()

    st.write("### " + question["question"])

    # Перемешивание вариантов
    # Создаём список индексов для options и перемешиваем их
    option_indices = list(range(len(question["options"])))
    random.shuffle(option_indices)

    # Используем radio с перемешанными индексами
    choice_idx_in_shuffled = st.radio(
        "Выберите ответ:",
        options=option_indices,
        format_func=lambda x: question["options"][x],
        key=f"q_{st.session_state.current}" # Уникальный ключ для каждого вопроса
    )

    if st.button("Ответить"):
        # Проверяем, был ли выбран ответ
        if choice_idx_in_shuffled is not None:
            # Засекаем время
            # Сохраняем время по индексу в *экзамене* (st.session_state.current), а не по индексу в cards
            st.session_state.time_per_question[st.session_state.current] = int(time.time() - question_start)
            # Сохраняем выбранный *индекс* варианта из *оригинального* вопроса
            st.session_state.answers[st.session_state.current] = choice_idx_in_shuffled

            if choice_idx_in_shuffled == question["correct"]:
                st.success("Правильно!")
                st.session_state.score += 1
            else:
                st.error("Неверно!")
                st.write(f"Правильный ответ: {question['options'][question['correct']]}")

            # Кнопка "Следующий" появляется после "Ответить"
            if st.button("Следующий"):
                st.session_state.current += 1
                # st.rerun() предпочтительнее для новых версий Streamlit
                st.rerun()
        else:
            st.warning("Пожалуйста, выберите ответ.")
