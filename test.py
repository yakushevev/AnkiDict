"""
Тестовый скрипт для модуля CSVParser.
"""
import sys
import os

# Добавляем путь к модулю, если он находится в другой директории
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from csv_parser import CSVParser
from anki_generator import AnkiGenerator

def main():
    # Создаем экземпляр парсера
    parser = CSVParser()
    parser.parse_first_csv('words.csv')
    parser.parse_second_csv('translate.csv')
    anki_generator = AnkiGenerator(parser, None)
    # Пример использования с тестовыми данными
    # В реальном случае здесь будут пути к вашим CSV файлам
    
    # Для демонстрации результатов, мы можем создать временные данные
    print("=== Тестирование CSVParser ===\n")
    
    # Проверка на наличие методов
    print("1. Методы класса:")
    methods = [method for method in dir(parser) if not method.startswith('_')]
    for method in sorted(methods):
        print(f"   - {method}")
    
    # Проверка начальных данных
    print("\n2. Начальные данные:")
    print(f"   Слова: {list(parser.all_words_data.keys())}")
    print(f"   Произношения: {dict(parser.pron_to_chars)}")
    print(f"   Иероглифы по произношению: {dict(parser.char_to_pron)}")
    print(f"   Слова по иероглифам: {dict(parser.char_to_words)}")
    
    # Тестирование получения анализа для конкретных иероглифов
    print("\n3. Анализ иероглифов:")
    
    test_chars = ['准', '备', '历', '史']
    for char in test_chars:
        analysis = parser.get_char_analysis(char)
        print(f"\n   Для иероглифа '{char}':")
        print(f"     Слова с этим иероглифом: {analysis['words']}")
        print(f"     Омофоны (те же строки): {analysis['chars_with_same_pronunciation']}")

    # Примеры работы с конкретными словами
    print("\n4. Данные по словам:")
    
    test_words = ['准备', '历史']
    for word in test_words:
        data = parser.get_word_data(word)
        print(f"\n   Слово '{word}':")
        if data:
            for key, value in data.items():
                print(f"     {key}: {value}")
            print(f"     Карта: {anki_generator.generate_back_html(word, data)}")
        else:
            print(f"     Данные не найдены")
        

if __name__ == "__main__":
    main()