from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, jsonify
from flask_cors import CORS
from database import get_db_connection, ensure_user_exists, insert_query, insert_response
from nlp_module import process_query

app = Flask(__name__)
CORS(app)

@app.route('/api/process', methods=['POST'])
def process_input():
    data = request.get_json()
    user_id = data.get('user_id')
    input_text = data.get('input_text')

    if not user_id or not input_text:
        return jsonify({"error": "Отсутствует user_id или текст ввода"}), 400

    try:
        # Получаем ответ, предмет и литературу из nlp_module
        query_response, subject, literature = process_query(input_text)
        
        # Получаем рекомендации
        conn = get_db_connection()
        ensure_user_exists(conn, user_id)
        query_id = insert_query(conn, user_id, input_text)
        if query_response:
            insert_response(conn, query_id, query_response)
        
        cur = conn.cursor()
        cur.execute(
            "SELECT recommendation_text, timestamp FROM Recommendations WHERE user_id = %s ORDER BY timestamp DESC LIMIT 10",
            (user_id,)
        )
        recommendations = cur.fetchall()
        cur.close()
        conn.close()
        
        response = {
            "query_response": query_response,
            "recommendations": recommendations,
            "literature": literature
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)