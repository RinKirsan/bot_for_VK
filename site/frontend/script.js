document.addEventListener("DOMContentLoaded", function() {
    fetchData(); // Fetch data when the page loads
});

function fetchData() {
    // Fetch data from the backend (replace 'http://localhost:3000' with your backend URL)
    fetch('http://localhost:3000/data')
        .then(response => response.json())
        .then(data => {
            // Display data
            displayData(data);
        })
        .catch(error => console.error('Error fetching data:', error));
}

function displayData(data) {
    const imageListDiv = document.getElementById('imageList');
    imageListDiv.innerHTML = '';

    // Iterate through data and create HTML elements for each item
    data.forEach(item => {
        const div = document.createElement('div');
        div.classList.add('item-container'); // Добавляем класс для стилизации через CSS

        // Создаем элемент чекбокса
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.name = 'selectedItem'; // Устанавливаем имя для группировки
        checkbox.value = JSON.stringify({ image: item.image, text: item.text }); // Передаем объект с именем изображения и текстом

        // Создаем элемент изображения
        const img = document.createElement('img');
        img.src = item.image;
        img.alt = item.text;

        // Создаем элемент текста
        const p = document.createElement('p');
        p.textContent = item.text;

        // Добавляем чекбокс, изображение и текст к родительскому элементу
        // Создаем элементы в следующем порядке: чекбокс, изображение, текст
		div.appendChild(checkbox);
		div.appendChild(img);
		div.appendChild(p);


        // Добавляем созданный элемент к списку изображений
        imageListDiv.appendChild(div);
    });
}




function publishToVK() {
    // Get all selected checkboxes
    const selectedCheckboxes = document.querySelectorAll('input[name=selectedItem]:checked');
    
    // Collect the values of selected checkboxes
    const selectedItems = Array.from(selectedCheckboxes).map(checkbox => JSON.parse(checkbox.value)); // Парсим JSON строку обратно в объект

    // Make a POST request to your backend with selected items
    fetch('http://localhost:3000/publish', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ selectedItems: selectedItems })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Published to VK:', data);
    })
    .catch(error => console.error('Error publishing to VK:', error));
}

