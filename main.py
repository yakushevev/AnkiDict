"""
Основной скрипт для генерации словаря Anki из CSV файлов.
"""
import argparse
import sys
import os
from pathlib import Path
from csv_parser import CSVParser
from tts_handler import TTSHandler
from anki_generator import AnkiGenerator

# Устанавливаем кодировку UTF-8 для консоли Windows
if sys.platform == 'win32':
    import io
    # Устанавливаем переменную окружения для Python
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    # Перенаправляем stdout и stderr с правильной кодировкой
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    # Устанавливаем кодировку консоли Windows на UTF-8
    try:
        os.system('chcp 65001 >nul 2>&1')
    except:
        pass


def main():
    """Основная функция."""
    parser = argparse.ArgumentParser(
        description='Генератор словарей Anki из CSV файлов'
    )
    parser.add_argument(
        'csv1',
        type=str,
        help='Путь к первому CSV файлу (слова и иероглифы)'
    )
    parser.add_argument(
        'csv2',
        type=str,
        help='Путь ко второму CSV файлу (переводы)'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='chinese_dict.apkg',
        help='Имя выходного файла .apkg (по умолчанию: chinese_dict.apkg)'
    )
    parser.add_argument(
        '-d', '--deck-name',
        type=str,
        default='Chinese Dictionary',
        help='Название колоды Anki (по умолчанию: Chinese Dictionary)'
    )
    parser.add_argument(
        '--audio-dir',
        type=str,
        default='audio_cache',
        help='Директория для кэширования аудио файлов (по умолчанию: audio_cache)'
    )
    
    args = parser.parse_args()
    
    # Проверяем существование файлов
    csv1_path = Path(args.csv1)
    csv2_path = Path(args.csv2)
    
    if not csv1_path.exists():
        print(f"Ошибка: файл {args.csv1} не найден!")
        sys.exit(1)
    
    if not csv2_path.exists():
        print(f"Ошибка: файл {args.csv2} не найден!")
        sys.exit(1)
    
    print("Парсинг CSV файлов...")
    
    # Парсим CSV файлы
    csv_parser = CSVParser()
    csv_parser.parse_first_csv(str(csv1_path))
    csv_parser.parse_second_csv(str(csv2_path))
    
    words_count = len(csv_parser.get_all_words())
    print(f"Найдено {words_count} уникальных слов")
    
    if words_count == 0:
        print("Ошибка: не найдено ни одного слова!")
        sys.exit(1)
    
    # Инициализируем TTS
    print("\nИнициализация TTS...")
    tts_handler = TTSHandler(audio_dir=args.audio_dir)
    
    # Генерируем колоду Anki
    print("\nГенерация колоды Anki...")
    anki_generator = AnkiGenerator(csv_parser, tts_handler)
    anki_generator.generate_deck(
        deck_name=args.deck_name,
        output_file=args.output
    )
    
    print("\nГотово!")


if __name__ == '__main__':
    main()
