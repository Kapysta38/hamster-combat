function connectWebSocket() {
    const countElement = document.getElementById('count');
    const incrementButton = document.getElementById('incrementButton');
    const loadingSpinner = document.getElementById('loading');

    if (!countElement || !incrementButton || !loadingSpinner) {
        console.error("Elements with IDs 'count', 'incrementButton' or 'loading' not found in DOM.");
        return;
    }

    // Показ загрузочного спиннера и скрытие счетчика
    loadingSpinner.classList.add('show-loading');
    countElement.style.display = 'none';

    const socket = new WebSocket("wss://hamstersd.ru/ws");

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'count') {
            countElement.textContent = data.value;
            // Скрыть загрузку и показать счётчик при первом обновлении
            loadingSpinner.classList.remove('show-loading');
            countElement.style.display = 'block';
        }
    };

    socket.onclose = () => {
        console.log("Connection closed, retrying...");
        setTimeout(connectWebSocket, 1000);
    };

    incrementButton.addEventListener('click', (event) => {
        if (socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ type: 'increment' }));
        }
        showIncrementAnimation(event);
    });
}

function showIncrementAnimation(event) {
    const container = document.querySelector('.container');
    const increment = document.createElement('span');
    increment.className = 'increment-animation';
    increment.textContent = '+1';

    // Позиция элемента на основе клика
    increment.style.left = `${event.clientX - 20}px`;
    increment.style.top = `${event.clientY - 20}px`;

    container.appendChild(increment);

    // Удаление элемента после анимации
    setTimeout(() => {
        container.removeChild(increment);
    }, 1000);
}

window.onload = connectWebSocket;


