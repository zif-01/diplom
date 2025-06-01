const API_BASE_URL = 'http://localhost:5000/api';

async function processInput() {
    const inputField = document.getElementById('input-field').value;
    const responseArea = document.getElementById('response-area');
    const statusArea = document.getElementById('status-area');

    if (!inputField) {
        statusArea.textContent = 'Ошибка: Введите запрос или предмет.';
        return;
    }

    statusArea.textContent = 'Обработка...';
    responseArea.innerHTML = '';

    try {
        const response = await fetch(`${API_BASE_URL}/process`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: 1, input_text: inputField })
        });
        const data = await response.json();

        if (response.ok) {
            // Ответ на запрос (если не null)
            if (data.query_response) {
                const queryHeader = document.createElement('h3');
                queryHeader.textContent = 'Ответ на запрос';
                queryHeader.className = 'text-lg font-semibold mb-2 text-white';
                responseArea.appendChild(queryHeader);
                const queryP = document.createElement('p');
                queryP.textContent = data.query_response;
                queryP.className = 'text-gray-300 mb-4';
                responseArea.appendChild(queryP);
            }

            // Рекомендации
            if (data.recommendations.length > 0) {
                const recHeader = document.createElement('h3');
                recHeader.textContent = 'Рекомендации';
                recHeader.className = 'text-lg font-semibold mb-2 text-white';
                responseArea.appendChild(recHeader);
                data.recommendations.forEach(rec => {
                    const p = document.createElement('p');
                    p.textContent = `${rec.recommendation_text} (Дата: ${new Date(rec.timestamp).toLocaleString()})`;
                    p.className = 'text-gray-300 mb-1';
                    responseArea.appendChild(p);
                });
            }

            // Литература
            if (data.literature && data.literature.length > 0) {
                const litHeader = document.createElement('h3');
                litHeader.textContent = 'Рекомендованная литература';
                litHeader.className = 'text-lg font-semibold mb-2 mt-4 text-white';
                responseArea.appendChild(litHeader);
                data.literature.forEach(item => {
                    const p = document.createElement('p');
                    p.innerHTML = `<strong>${item.title}</strong> (${item.author}) - ${item.subject}${item.url ? `<br><a href="${item.url}" target="_blank" class="text-purple-400 hover:text-purple-300">Ссылка</a>` : ''}`;
                    p.className = 'text-gray-300 mb-2';
                    responseArea.appendChild(p);
                });
            }

            // Если ничего не найдено
            if (!data.query_response && data.recommendations.length === 0 && (!data.literature || data.literature.length === 0)) {
                responseArea.textContent = 'Результаты не найдены.';
            }

            statusArea.textContent = 'Обработка завершена.';
        } else {
            statusArea.textContent = `Ошибка сервера: ${data.error} (Код: ${response.status})`;
            responseArea.textContent = 'Произошла ошибка при обработке.';
        }
    } catch (error) {
        statusArea.textContent = `Ошибка сети: ${error.message}. Проверьте, работает ли сервер на ${API_BASE_URL}.`;
        responseArea.textContent = 'Не удалось подключиться к серверу.';
        console.error('Детали ошибки:', error);
    }
}

document.getElementById('submit-btn').addEventListener('click', processInput);