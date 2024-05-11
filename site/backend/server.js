const express = require('express');
const session = require('express-session');
const path = require('path');
const xlsx = require('xlsx');
const bodyParser = require('body-parser');
const fs = require('fs');
/*
const https = require('https');
const fs = require('fs');

const options = {
    key: fs.readFileSync('key.pem'),
    cert: fs.readFileSync('cert.pem')
};*/

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

    // Чтение существующего файла new_data.xlsx
    const existingWorkbook = xlsx.readFile(path.join(__dirname, '..', 'new_data.xlsx'));
    const existingSheet = existingWorkbook.Sheets[existingWorkbook.SheetNames[0]];

    // Заполнение новых данных в существующем листе
    selectedItems.forEach(item => {
        const { image, text } = item;
        const rowIndex = existingSheet['!rows'] ? existingSheet['!rows'].length : 0;
        xlsx.utils.sheet_add_aoa(existingSheet, [[text, image]], { origin: -1, rowIndex: rowIndex });
    });

    // Сохранение изменений в существующем файле new_data.xlsx
    xlsx.writeFile(existingWorkbook, path.join(__dirname, '..', 'new_data.xlsx'));

    // Удаление выбранных данных из data.xlsx
    const dataWorkbook = xlsx.readFile(path.join(__dirname, '..', 'data.xlsx'));
    const dataSheet = dataWorkbook.Sheets[dataWorkbook.SheetNames[0]];
    selectedItems.forEach(item => {
        const { text } = item;
        for (const cellAddress in dataSheet) {
            if (cellAddress.startsWith('A') && dataSheet[cellAddress].v === text) {
                const rowNumber = parseInt(cellAddress.substring(1));
                delete dataSheet[`A${rowNumber}`];
                delete dataSheet[`B${rowNumber}`];
                break; // выходим из цикла, после удаления одной строки
            }
        }
    });
    // Сохранение изменений в data.xlsx
    xlsx.writeFile(dataWorkbook, path.join(__dirname, '..', 'data.xlsx'));

    res.json({ message: 'Data saved successfully.', newFilePath: path.join(__dirname, '..', 'new_data.xlsx') });
});


app.post('/del', isAuthenticated, (req, res) => {
    const { selectedItems } = req.body;
    // Удаление выбранных данных из data.xlsx
    const dataWorkbook = xlsx.readFile(path.join(__dirname, '..', 'data.xlsx'));
    const dataSheet = dataWorkbook.Sheets[dataWorkbook.SheetNames[0]];
    selectedItems.forEach(item => {
        const { text } = item;
        for (const cellAddress in dataSheet) {
            if (cellAddress.startsWith('A') && dataSheet[cellAddress].v === text) {
                const rowNumber = parseInt(cellAddress.substring(1));
                delete dataSheet[`A${rowNumber}`];
                delete dataSheet[`B${rowNumber}`];
                break; // выходим из цикла, после удаления одной строки
            }
        }
    });
    // Сохранение изменений в data.xlsx
    xlsx.writeFile(dataWorkbook, path.join(__dirname, '..', 'data.xlsx'));
    
    res.json({ message: 'Data saved successfully.', newFilePath: path.join(__dirname, '..', 'new_data.xlsx') });
});


// Сервер статических файлов из папки frontend
app.use(express.static(path.join(__dirname, '..', 'frontend')));

// Сервер статических файлов из папки images

app.use(express.static(path.join(__dirname, '..', 'images')));

/*https.createServer(options, app).listen(443, () => {
    console.log(`Server is running on port 443`);
});*/

// Запуск сервера
app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});
