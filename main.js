import fs from "fs";
import path from "path";
import fetch from "node-fetch";
import FormData from "form-data";






const apiKey = 'ЗАМЕНИТЬ_НА_ТОКЕН'; // Замените на ваш ключ API








const dirPath = './'; 

async function transcribeAudio(filePath) {
    try {
        // Читаем аудиофайл в буфер
        const audioBuffer = fs.readFileSync(filePath);

        // Создаем объект FormData и добавляем файл
        const formData = new FormData();
        formData.append('file', audioBuffer, path.basename(filePath));
        formData.append('model', 'whisper-1');
        formData.append('language', 'RU');

        const startTime = Date.now();

        // Отправляем запрос к API
        const response = await fetch('https://api.deep-foundation.tech/v1/audio/transcriptions', {
            method: 'POST',
            headers: {
                Authorization: `Bearer ${apiKey}`,
                ...formData.getHeaders(),
            },
            body: formData,
        });

        const responseData = await response.json();
        const endTime = Date.now();

        const tokensUsed = responseData.input_length_ms; // Если используется метрика токенов
        const duration = (endTime - startTime) / 1000; // Время транскрибации в секундах

        const audioStats = fs.statSync(filePath);
        const audioLength = audioStats.size; // Длина аудиофайла в байтах

        console.log(`Транскрибирован файл: ${filePath}`);
        console.log(`Количество токенов: ${tokensUsed}`);
        console.log(`Время транскрибации: ${duration.toFixed(2)} секунды`);
        console.log(`Длина аудиозаписи: ${(responseData.input_length_ms / 1000).toFixed(1)} секунды`);
        //console.log(responseData.inference_status.runtime_ms);
        console.log(`///////////////////////////////////////`);

        // Создание текстового файла с транскрибацией
        const outputFilePath = path.join(path.dirname(filePath), `${path.basename(filePath, path.extname(filePath))}.txt`);
        //const outputData = `Количество токенов: ${tokensUsed}\nВремя транскрибации: ${duration.toFixed(2)} секунды\nДлина аудиофайла: ${(responseData.input_length_ms / 1000).toFixed(1)} секунды\n\n${responseData.text}`;

        fs.writeFileSync(outputFilePath, responseData.text);
    } catch (error) {
        console.error(`Ошибка транскрибации файла ${filePath}: ${error.message}`);
    }
}

async function transcribeAllAudioFiles() {
    fs.readdir(dirPath, (err, files) => {
        if (err) {
            return console.error(`Ошибка при чтении директории: ${err.message}`);
        }

        const audioFiles = files.filter(file => ['.mp3', '.wav', '.ogg', '.m4a'].includes(path.extname(file).toLowerCase()));

        audioFiles.forEach(file => {
            const filePath = path.join(dirPath, file);
            transcribeAudio(filePath);
        });
    });
}

transcribeAllAudioFiles();
