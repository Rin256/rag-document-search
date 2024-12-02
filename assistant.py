import argparse
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import openai
from dotenv import load_dotenv
import os
import re
import csv
from filelock import FileLock
from datetime import datetime
import uuid
import json

class Assistant:
    NEGATIVE_ANSWER = "Не удалось найти ответ в предоставленном источнике."
    PROMPT_TEMPLATE = f"""Ты помощник для ответов на вопросы.
Не придумывай ответ. Если не знаешь ответа, просто скажи: «{NEGATIVE_ANSWER}»
Отвечай на вопрос, основываясь только на следующем контексте:

{{context}}

---

Ответь на вопрос, исходя из приведенного выше контекста: {{question}}"""
    
    def __init__(self, chroma_path="chroma", log_dir="logs"):
        openai.api_key = os.environ['OPENAI_API_KEY']
        embedding_function = OpenAIEmbeddings(model="text-embedding-3-large")
        self.db = Chroma(persist_directory=chroma_path, embedding_function=embedding_function)
        self.chroma_path = chroma_path
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)

    def generate(self, question):
        # Основная логика для поиска в базе данных и генерации ответа
        chunks = self.search_database(question)
        responses = []

        # Генерация ответа по схожести
        formatted_similarity_response = self.format_similarity_response(chunks)
        responses.append(formatted_similarity_response)
             
        # Генерация ответа для каждого файла из контекста отдельно
        for chunk in chunks:
            prompt = self.create_prompt([chunk], question)  # Используем только один файл
            response = self.get_response(prompt)
            formatted_gpt_response = self.format_gpt_response(response, chunk)
            if formatted_gpt_response:
                responses.append(formatted_gpt_response)
        
        general_response = "\n__\n\n".join(responses)
        print(general_response)
        return general_response

    def search_database(self, question):
        # Поиск в базе данных релевантных документов
        chunks = self.db.similarity_search_with_relevance_scores(question, k=10)
        return chunks

    def create_prompt(self, chunks, question):
        # Создание промпта из шаблона
        context = "\n\n---\n\n".join([chunk.page_content for chunk, _score in chunks])
        prompt_template = ChatPromptTemplate.from_template(self.PROMPT_TEMPLATE)
        return prompt_template.format(context=context, question=question)

    def get_response(self, prompt):
        # Генерация ответа с использованием модели
        model = ChatOpenAI(model="gpt-4o", temperature=1)
        response = model.invoke(prompt)

        # Получение информации о запросе
        input_tokens = response.response_metadata['token_usage']['prompt_tokens']
        output_tokens = response.response_metadata['token_usage']['completion_tokens']
        total_tokens = response.response_metadata['token_usage']['total_tokens']
        model_name = response.response_metadata['model_name']

        # Получение текущей даты и времени
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Генерация уникального идентификатора
        unique_id = str(uuid.uuid4())

        # Запись информации в CSV файл
        csv_file_path = os.path.join(self.log_dir, "query_logs.csv")
        data = [unique_id, current_time, input_tokens, output_tokens, total_tokens, model_name]
        self.write_to_csv(csv_file_path, data)

        # Запись вопроса и ответа в JSON файл
        log_data = {
            "prompt": prompt,
            "response": response.content
        }
        json_file_path = os.path.join(self.log_dir, f"{unique_id}.json")
        with open(json_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(log_data, json_file, ensure_ascii=False, indent=4)

        return response.content

    def write_to_csv(self, file_path, data):
        lock = FileLock(f"{file_path}.lock")
        with lock:
            file_exists = os.path.isfile(file_path)
            with open(file_path, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                if not file_exists:
                    # Записываем заголовок, если файл создается впервые
                    writer.writerow(["id", "date", "input_tokens", "output_tokens", "total_tokens", "model_name"])
                writer.writerow(data)

    def format_similarity_response(self, chunks):
        # Извлечение и форматирование имен источников с оценкой схожести
        sources = [
            self.format_source(chunk.metadata.get("source", None), score)
            for chunk, score in chunks
        ]
        return "\n".join(sources)
    
    def format_source(self, source, score):
        # Проверяем, есть ли ссылка и соответствует ли она ожидаемому формату
        if source and re.match(r"data\\.*\.md", source):
            # Преобразуем путь к нужному формату
            # Убираем 'data\\' и '.md'
            formatted_source = re.sub(r'data\\', '', source)
            formatted_source = formatted_source.replace('.md', '')
            # Включаем оценку схожести
        else:
            formatted_source = source
        return f"{formatted_source} (схожесть: {score:.2f})"
    
    def format_gpt_response(self, response, chunk):
        # Форматирование текста ответа с указанием источника и балла
        if response == self.NEGATIVE_ANSWER:
            return ""
        
        document, score = chunk # Разбираем кортеж на объект и оценку
        source = document.metadata.get("source", None)
        formatted_source = self.format_source(source, score)
        return f"Источник: {formatted_source}\n\n{response}"


if __name__ == "__main__":
   # Загрузка переменных окружения из файла .env
   load_dotenv()

   # Чтение текста запроса
   parser = argparse.ArgumentParser()
   parser.add_argument("question", type=str, help="The query text.")
   args = parser.parse_args()
   question = args.question

   # Создание экземпляра Assistant и его запуск
   assistant = Assistant()
   assistant.generate(question)
