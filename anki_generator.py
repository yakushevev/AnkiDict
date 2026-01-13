"""
Модуль для генерации карточек Anki в формате .apkg.
"""
import genanki
import csv
import hashlib
from typing import Dict, List
from pathlib import Path
from csv_parser import CSVParser
from tts_handler import TTSHandler


class AnkiGenerator:
    """Класс для генерации карточек Anki."""
    
    def __init__(self, parser: CSVParser, tts_handler: TTSHandler):
        """
        Инициализация генератора Anki.
        
        Args:
            parser: Парсер CSV файлов
            tts_handler: Обработчик TTS
        """
        self.parser = parser
        self.tts_handler = tts_handler
        
        # Списки для отслеживания слов без перевода и ошибок обработки
        self.words_without_translation = []
        self.processing_errors = []
        
        # Создаем модель карточки
        self.model = genanki.Model(
            1607392319,  # Уникальный ID модели
            'Chinese Dictionary Model',
            fields=[
                {'name': 'Word'},
                {'name': 'Pronunciation'},
                {'name': 'Front'},
                {'name': 'Back'},
                {'name': 'Examples'},
                {'name': 'Audio'},
            ],
            templates=[
                {
                    'name': 'Card 1 (Front → Back)',
                    'qfmt': '{{Front}}',
                    'afmt': '{{FrontSide}}<hr id="answer">{{Back}}{{Examples}}',
                },
                {
                    'name': 'Card 2 (Back → Front)',
                    'qfmt': '{{Back}}',
                    'afmt': '{{FrontSide}}<hr id="answer">{{Front}}{{Examples}}',
                },
            ],
            css='''
            .card {
                font-family: Arial, sans-serif;
                font-size: 20px;
                text-align: center;
                color: #333;
            }
            .word {
                font-size: 48px;
                font-weight: bold;
                margin: 40px 0;
                color: #2c3e50;
            }
            .pronunciation {
                font-size: 24px;
                color: #7f8c8d;
                margin-top: 20px;
            }
            .translations {
                text-align: left;
                margin: 20px 0;
            }
            .translation-type {
                font-weight: bold;
                color: #3498db;
                margin-top: 15px;
            }
            .translation-meaning {
                margin-left: 20px;
                margin-top: 5px;
            }
            .character-analysis {
                text-align: left;
                margin: 20px 0;
                border-top: 2px solid #ecf0f1;
                padding-top: 20px;
            }
            .char-item {
                margin: 15px 0;
            }
            .char-title {
                font-weight: bold;
                font-size: 28px;
                color: #2c3e50;
                margin-bottom: 10px;
            }
            .char-words, .char-pronunciation {
                margin-left: 20px;
                margin-top: 5px;
                color: #555;
            }
            '''
        )
    
    def generate_front_html(self, word: str, pronunciation: str) -> str:
        """
        Генерирует HTML для лицевой стороны карточки.
        
        Args:
            word: Слово
            pronunciation: Произношение
            
        Returns:
            HTML строка
        """
        audio_path = self.tts_handler.get_audio_path(word)
        audio_tag = f'[sound:{Path(audio_path).name}]' if audio_path and Path(audio_path).exists() else ''
        
        pron_html = f'<div class="pronunciation">{pronunciation}</div>' if pronunciation else ''
        
        html = f'''
        <div class="word">{word}</div>
        {pron_html}
        {audio_tag}
        '''
        return html.strip()
    
    def generate_back_html(self, word: str, word_data: Dict) -> str:
        """
        Генерирует HTML для оборотной стороны карточки.
        
        Args:
            word: Слово
            
        Returns:
            HTML строка
        """
        html_parts = []
        
        # 1. Переводы
        translations = word_data.get('translations', {})
        if translations:
            html_parts.append('<div class="translations">')
            for word_type, meanings in translations.items():
                if meanings:
                    html_parts.append(f'<div class="translation-type">{word_type}:</div>')
                    for meaning in meanings:
                        if meaning.strip():
                            html_parts.append(f'<div class="translation-meaning">• {meaning.strip()}</div>')
            html_parts.append('</div>')
        
        return ''.join(html_parts)
    
    def generate_examples_html(self, word: str, word_data: Dict) -> str:
        """
        Генерирует HTML для оборотной стороны карточки.
        
        Args:
            word_data: Данные о слове
            
        Returns:
            HTML строка
        """
        html_parts = []
        
        # 2. Разбор иероглифов
        characters = word_data.get('characters', [])
        if characters:
            html_parts.append('<div class="character-analysis">')
            for char in characters:
                analysis = self.parser.get_char_analysis(char, word)
                
                html_parts.append(f'<div class="char-item">')
                html_parts.append(f'<div class="char-title">{char}</div>')
                
                # Слова с таким же иероглифом
                words_with_char = analysis.get('words', [])
                # Исключаем само слово из списка
                words_with_char = [w for w in words_with_char if w != word]
                if words_with_char:
                    words_str = ', '.join(words_with_char[:10])  # Ограничиваем до 10 слов
                    html_parts.append(f'<div class="char-words">Употребление: {words_str}</div>')
                
                # Иероглифы с идентичным звучанием
                chars_with_same_pron = analysis.get('chars_with_same_pronunciation', [])
                # Исключаем сам иероглиф из списка
                chars_with_same_pron = [c for c in chars_with_same_pron if c != char]
                if chars_with_same_pron:
                    chars_str = ', '.join(chars_with_same_pron[:10])  # Ограничиваем до 10
                    html_parts.append(f'<div class="char-pronunciation">Однозвучные: {chars_str}</div>')
                 
                html_parts.append('</div>')
                
            if 'wordHomophones' in word_data and word_data['wordHomophones']: 
                wordHomophonesStr=', '.join(word_data['wordHomophones'])
                html_parts.append(f'<div class="char-pronunciation">Слова, звучащие также: {wordHomophonesStr}</div>')
            html_parts.append('</div>')
        
                
        
        return ''.join(html_parts)
    
    def add_word_without_translation(self, word: str, pronunciation: str = ""):
        """Добавляет слово без перевода в список."""
        self.words_without_translation.append({
            'word': word,
            'pronunciation': pronunciation
        })

    def add_processing_error(self, word: str, error: str):
        """Добавляет слово с ошибкой обработки в список."""
        self.processing_errors.append({
            'word': word,
            'error': error
        })

    def generate_words_without_translation_csv(self, filename: str = "words_without_translation.csv"):
        """Генерирует CSV файл для слов без перевода."""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['word', 'pronunciation']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for item in self.words_without_translation:
                writer.writerow(item)
        print(f"Файл '{filename}' сгенерирован с {len(self.words_without_translation)} словами без перевода.")

    def generate_processing_errors_csv(self, filename: str = "processing_errors.csv"):
        """Генерирует CSV файл для слов с ошибками обработки."""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['word', 'error']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for item in self.processing_errors:
                writer.writerow(item)
        print(f"Файл '{filename}' сгенерирован с {len(self.processing_errors)} ошибками обработки.")

    def generate_deck(self, deck_name: str = "Chinese Dictionary", output_file: str = "chinese_dict.apkg"):
        """
        Генерирует колоду Anki.
        
        Args:
            deck_name: Название колоды
            output_file: Имя выходного файла
        """
        deck = genanki.Deck(
            2059400110,  # Уникальный ID колоды
            deck_name
        )
        
        words = self.parser.get_all_words()
        print(f"Генерация карточек для {len(words)} слов...")
        
        skipped_count = 0
        skipped_words = []
        
        for i, word in enumerate(words, 1):
            if i % 10 == 0:
                print(f"Обработано {i}/{len(words)} слов...")
            
            word_data = self.parser.get_word_data(word)
            
            # Проверяем наличие переводов
            translations = word_data.get('translations', {})
            if not translations or not any(translations.values()):
                skipped_count += 1
                skipped_words.append(word)
                # Добавляем слово без перевода в список
                pronunciation = word_data.get('pronunciation', '')
                self.add_word_without_translation(word, pronunciation)
                continue
            
            pronunciation = word_data.get('pronunciation', '')
            
            
            wordHomophones = []
            for other_word in words:
                if other_word!= word and self.parser.all_words_data[other_word]['pronunciation']==word_data['pronunciation']:
                    wordHomophones.append(other_word)
            word_data['wordHomophones'] = wordHomophones
            
            # Генерируем HTML
            front_html = self.generate_front_html(word, pronunciation)
            back_html = self.generate_back_html(word, word_data)
            examples_html = self.generate_examples_html(word, word_data)
            
            # Получаем путь к аудио
            audio_path = self.tts_handler.get_audio_path(word)
            audio_path = ''
            audio_field = Path(audio_path).name if audio_path else ''
            
            # Создаем заметку
            # Генерируем GUID на основе содержимого карточки для предотвращения дубликатов
            guid_content = f"{word}|{pronunciation}|{front_html}|{back_html}|{examples_html}"
            guid = hashlib.md5(guid_content.encode('utf-8')).hexdigest()
            
            note = genanki.Note(
                model=self.model,
                fields=[
                    word,
                    pronunciation,
                    front_html,
                    back_html,
                    examples_html,
                    audio_field
                ],
                guid=guid
            )
            
            deck.add_note(note)
        
        # Добавляем аудио файлы в пакет
        package = genanki.Package(deck)
        audio_files = []
        # Собираем аудио только для слов, которые были добавлены в колоду
        added_words = [w for w in words if w not in skipped_words]
        for word in added_words:
            audio_path = self.tts_handler.get_audio_path(word)
            if audio_path and Path(audio_path).exists():
                audio_files.append(audio_path)
        
        if audio_files:
            package.media_files = audio_files
        
        # Сохраняем колоду
        package.write_to_file(output_file)
        
        # Выводим статистику
        total_cards = len(words) - skipped_count
        print(f"\nКолода сохранена в файл: {output_file}")
        print(f"Сгенерировано карточек: {total_cards}")
        if skipped_count > 0:
            print(f"Пропущено карточек (без перевода): {skipped_count}")
            if len(skipped_words) <= 20:
                print(f"Пропущенные слова: {', '.join(skipped_words)}")
            else:
                print(f"Пропущенные слова (первые 20): {', '.join(skipped_words[:20])}...")
        
        # Генерируем CSV файлы
        self.generate_words_without_translation_csv()
        self.generate_processing_errors_csv()
