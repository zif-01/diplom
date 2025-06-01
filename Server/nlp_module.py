import spacy
import pymorphy3
from database import get_db_connection

nlp = spacy.load("ru_core_news_sm")
morph = pymorphy3.MorphAnalyzer()

def process_query(query_text):
    doc = nlp(query_text)
    # Извлекаем токены и нормализуем их
    keywords = [morph.parse(token.text.lower())[0].normal_form for token in doc if token.pos_ in ["NOUN", "VERB"]]
    
    # Извлечение предмета
    subject = None
    subjects = ["математика", "информатика", "физика", "программирование", "алгебра", "анализ", "дискретная"]
    for keyword in keywords:
        if keyword in subjects:
            subject = keyword.capitalize()
            break
    
    # Словарь соответствия предметов для поиска литературы
    subject_mapping = {
        "Математика": ["Линейная алгебра", "Математический анализ", "Алгебра"],
        "Информатика": ["Информатика", "Программирование", "Базы данных"],
        "Физика": ["Физика"],
        "Программирование": ["Программирование", "Информатика"],
        "Алгебра": ["Линейная алгебра", "Алгебра"],
        "Анализ": ["Математический анализ"],
        "Дискретная": ["Дискретная математика"]
    }
    
    # Словарь рекомендаций
    recommendations = {
        "экзамен": "Рекомендуется начать подготовку за 2 недели, изучить материалы курса и выполнить практические задания.",
        "домашнее задание": "Проверьте задания в системе, обратитесь к преподавателю за разъяснениями.",
        "расписание": "Ознакомьтесь с актуальным расписанием на портале университета или обратитесь в деканат.",
        "консультация": "Запишитесь на консультацию через систему или свяжитесь с преподавателем напрямую.",
        "материалы": "Скачайте учебные материалы из системы e-learning или запросите их у преподавателя.",
        "практика": "Для закрепления материала выполните практические задания и проверьте решения на платформе.",
        "мотивация": "Ставьте небольшие цели, делите задачи на части и вознаграждайте себя за успехи!",
        "проект": "Составьте план работы над проектом, обсудите этапы с руководителем и следуйте дедлайнам.",
        "литература": "Используйте рекомендованную литературу из учебного плана или обратитесь в библиотеку.",
        "группа": "Обсудите задание с одногруппниками или присоединитесь к учебной группе для совместной подготовки."
    }
    
    # Поиск литературы по ключевым словам и предмету
    literature = []
    if keywords or subject:
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            query = "SELECT id, title, author, subject, faculty, publication_year, url FROM Literature WHERE faculty = %s"
            params = ['Физико-математический, информационный и технологический']
            
            if keywords or subject:
                query += " AND ("
                conditions = []
                if keywords:
                    for keyword in keywords:
                        conditions.append(f"keywords ILIKE %s")
                        params.append(f'%{keyword}%')
                if subject and subject in subject_mapping:
                    # Добавляем связанные предметы
                    related_subjects = subject_mapping[subject]
                    for rel_subject in related_subjects:
                        conditions.append(f"subject ILIKE %s")
                        params.append(f'%{rel_subject}%')
                query += " OR ".join(conditions)
                query += ")"
            
            cur.execute(query, params)
            literature = cur.fetchall()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Ошибка при получении литературы: {e}")
    
    # Проверяем наличие ключевых слов для рекомендаций
    for keyword, response in recommendations.items():
        if keyword in keywords:
            return response, subject, literature
    
    # Если ничего не найдено, возвращаем None
    return None, subject, literature