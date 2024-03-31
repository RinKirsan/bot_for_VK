const express = require('express');
const session = require('express-session');
const path = require('path');
const xlsx = require('xlsx');
const bodyParser = require('body-parser');
const fs = require('fs');
const app = express();
const port = 3000;

// Установка сессий
app.use(session({
    secret: 'mySecretKey',
    resave: false,
    rolling: true, // Включаем rolling
    saveUninitialized: true,
    cookie: { maxAge: 1800000 } // Устанавливаем время жизни сессии 1000 = 1сек

}));

// Разрешение парсинга данных формы
app.use(bodyParser.urlencoded({ extended: true }));

// Массив с допустимым паролем
const validPassword = '123';

// Проверка аутентификации
function isAuthenticated(req, res, next) {
    if (req.session.authenticated) {
        return next();
    }
    res.redirect('/login');
}

// Маршрут для ввода пароля
app.get('/login', (req, res) => {
    res.sendFile(path.join(__dirname, '..', 'frontend', 'login.html'));
});

// Обработка отправленного пароля
app.post('/login', (req, res) => {
    const { password } = req.body;
    if (password === validPassword) {
        req.session.authenticated = true;
        res.redirect('/');
    } else {
        res.send('Invalid password');
    }
});

// Защищенный маршрут
app.get('/', isAuthenticated, (req, res) => {
    res.sendFile(path.join(__dirname, '..', 'frontend', 'index.html'));
});

// Определение конечной точки для получения данных
app.get('/data', isAuthenticated, (req, res) => {
    // Чтение данных из файла XLSX
    const workbook = xlsx.readFile(path.join(__dirname,'..', 'data.xlsx'));
    const sheetName = workbook.SheetNames[0];
    const worksheet = workbook.Sheets[sheetName];

    // Разбор данных из XLSX
    const data = xlsx.utils.sheet_to_json(worksheet);

    // Отправка данных в виде JSON-ответа
    res.json(data);
});

app.use(bodyParser.json()); // Добавляем middleware для обработки JSON данных

// Маршрут для сохранения данных в новый файл XLSX
app.post('/publish', isAuthenticated, (req, res) => {
    const { selectedItems } = req.body;

    // Проверка, есть ли выбранные элементы
    if (!selectedItems || !Array.isArray(selectedItems) || selectedItems.length === 0) {
        return res.status(400).send('No selected items or invalid data format.');
    }

    // Создание нового workbook
    const newWorkbook = xlsx.utils.book_new();
    const newSheet = xlsx.utils.aoa_to_sheet([['Image', 'Text']]);
    xlsx.utils.book_append_sheet(newWorkbook, newSheet, 'Sheet1');

    // Заполнение нового листа данными
    selectedItems.forEach(item => {
        const { image, text } = item;
        xlsx.utils.sheet_add_aoa(newSheet, [[image, text]], { origin: -1 });
    });

    // Сохранение нового файла XLSX
    const filePath = path.join(__dirname, '..', 'new_data.xlsx');
    xlsx.writeFile(newWorkbook, filePath);

    res.json({ message: 'Data saved successfully.', filePath: filePath });
});


// Сервер статических файлов из папки frontend
app.use(express.static(path.join(__dirname, '..', 'frontend')));

// Сервер статических файлов из папки images

app.use(express.static(path.join(__dirname, '..', 'images')));

// Запуск сервера
app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});
