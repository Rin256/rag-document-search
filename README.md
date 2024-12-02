# Рекомендации
Виртуальное окружение python позволит избежать ситуаций, когда разные приложения требуют разных пакетов.
Также это предотвращает загрязнение глобального каталога пакетов.
```cli
python -m venv venv :: Создание виртуального окружения
.\venv\Scripts\activate :: Подключение к виртуальному окружению
deactivate :: Отключение от вирутуального окружения
```

# Настройка окружения
1. Установить Microsoft C++ Build Tools (https://github.com/bycloudai/InstallVSBuildToolsWindows?tab=readme-ov-file)
2. Установить Microsoft Office
3. Установить Python 3.12 (https://www.python.org/downloads/)
4. Установить зависимости для python согласно файлу `requirements.txt`
```cli
python -m venv venv :: Создание виртуального окружения
.\venv\Scripts\activate :: Подключение к виртуальному окружению
pip install -r requirements.txt :: Установка необходимых библиотек python в вирутальном окружении
deactivate :: Отключение от вирутуального окружения
```
5. Включить VPN

# Подготовка данных
1. Поместить doc и docs файлы в каталог 'data_doc'. Запустить конвертирование doc в md.
Сконвертированные файлы будут помещены в каталог 'data'. Рекомендуется предварительно очистить каталог 'data'.
```cli
python document_converter.py
```
2. Создать векторную базу данных Chroma DB на основе файлов markdown из каталога 'data'. 
```cli
python chroma_generator.py
```

# Работа с приложением
1. Задавать вопросы gpt по векторной базе данных.
```cli
python assistant.py "Кодзима гений?"
```