
import streamlit as st
import json
import random
import time


# ===================== ЗАГРУЗКА ДАННЫХ =====================
@st.cache_data
def load_data():
    with open("db_test_66.json", "r", encoding="utf-8") as f:
        return json.load(f)

data = load_data()
cards = data["cards"]


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

    st.info("Объяснение:")
    st.write(q["options"][q["correct"]])

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
            st.session_state.order = list(range(len(cards)))
            random.shuffle(st.session_state.order)
            st.experimental_rerun()
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
            q = cards[i]

            st.write(f"### Вопрос {i+1}: {q['question']}")
            st.write(f"Ваш ответ: {q['options'][user_answer]}")
            st.write(f"Правильный: {q['options'][q['correct']]}")
            st.write(f"⏱ Время на вопрос: {st.session_state.time_per_question[i]} сек")
            st.write("---")

        if st.button("Пройти снова"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.experimental_rerun()

        st.stop()

    # ---------- Текущий вопрос ----------
    q_index = st.session_state.order[st.session_state.current]
    question = cards[q_index]

    st.write(f"Вопрос {st.session_state.current + 1} из {len(cards)}")

    # Прогресс
    st.progress((st.session_state.current + 1) / len(cards))

    # Таймер
    question_start = time.time()

    st.write("### " + question["question"])

    # Перемешивание вариантов
    shuffled = list(range(4))
    random.shuffle(shuffled)

    choice = st.radio("Выберите ответ:", shuffled,
                      format_func=lambda x: question["options"][x])

    if st.button("Ответить"):
        # Засекаем время
        st.session_state.time_per_question[q_index] = int(time.time() - question_start)
        st.session_state.answers[q_index] = choice

        if choice == question["correct"]:
            st.success("Правильно!")
            st.session_state.score += 1
        else:
            st.error("Неверно!")

        if st.button("Следующий"):
            st.session_state.current += 1
            st.experimental_rerun()
