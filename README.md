# Инструкция по работе с приложением

## Описание
Приложение служит для поиска информации в документах.
Для работы требуется каталог doc, docx файлов и интересующий вопрос.
Результатом служит список схожих файлов и ответ gpt по каждому из них, где модель нашла подходящую информацию. 

## Рекомендации
Виртуальное окружение python позволит избежать ситуаций, когда разные приложения требуют разных пакетов.
Также это предотвращает загрязнение глобального каталога пакетов.
```cli
python -m venv venv :: Создание виртуального окружения
.\venv\Scripts\activate :: Подключение к виртуальному окружению
deactivate :: Отключение от вирутуального окружения
```

## Настройка окружения
1. Установить Microsoft C++ Build Tools (https://github.com/bycloudai/InstallVSBuildToolsWindows?tab=readme-ov-file)
2. Установить Microsoft Office
3. Установить Python 3.12 (https://www.python.org/downloads/)
4. Установить зависимости для Python согласно файлу `requirements.txt`
```cli
pip install -r requirements.txt
```
5. Загрузить дополнительные ресурсы
```cli
python -c "import nltk; nltk.download('punkt_tab'); nltk.download('averaged_perceptron_tagger_eng')"
```
6. Создать файл '.env', где указать OpenAPI ключ аналогично примеру '.env.example'
7. Включить VPN

## Подготовка данных
1. Поместить doc и docs файлы в каталог 'data_doc'. Запустить конвертирование doc в md.
Сконвертированные файлы будут помещены в каталог 'data'. Рекомендуется предварительно очистить каталог 'data'.
```cli
python document_converter.py
```
2. Создать векторную базу данных Chroma на основе файлов markdown из каталога 'data'. 
```cli
python chroma_generator.py
```

## Поиск информации
1. Задавать вопросы gpt по векторной базе данных Chroma.
```cli
python assistant.py "Кодзима гений?"
```
