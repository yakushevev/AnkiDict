"""
Модуль для парсинга CSV файлов с данными о словах и переводах.
"""
import csv
from typing import Dict, List, Tuple, Set
from collections import defaultdict


class CSVParser:
    """Класс для парсинга CSV файлов."""
    
    def __init__(self):
        self.words_data: Dict[str, Dict] = {}  # слово -> данные
        self.pronunciations: Dict[str, str] = {}  # иероглиф -> произношение
        self.char_to_words: Dict[str, Set[str]] = defaultdict(set)  # иероглиф -> слова
        self.pron_to_chars: Dict[str, Set[str]] = defaultdict(set)  # произношение -> иероглифы
        self.char_homophones: Dict[str, Set[str]] = defaultdict(set)  # иероглиф -> омофоны (иероглифы из той же строки)
        self.seen_words: Set[str] = set()  # для отслеживания дубликатов
    
    def parse_first_csv(self, filepath: str):
        """
        Парсит первый CSV файл с данными о словах и иероглифах.
        Формат: первая_буква;произношение;иероглиф1;...;иероглиф9;слова1;...;слова5
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            # Определяем разделитель автоматически
            first_line = f.readline()
            f.seek(0)
            delimiter = ';' if ';' in first_line else ','
            reader = csv.reader(f, delimiter=delimiter)
            for row in reader:
                if len(row) < 2:
                    continue
                
                pronunciation = row[1].strip()
                if not pronunciation:
                    continue
                
                # Извлекаем иероглифы (колонки 2-10)
                characters = [char.strip() for char in row[2:11] if char.strip()]
                
                # Извлекаем слова (колонки 11-15)
                words_lists = [words.strip() for words in row[11:16] if words.strip()]
                
                # Сохраняем произношение для каждого иероглифа
                # Все иероглифы в одной строке - это омофоны (имеют одинаковое произношение)
                # ВАЖНО: сохраняем омофоны только если есть хотя бы 2 иероглифа в строке
                if len(characters) > 0:
                    for char in characters:
                        self.pronunciations[char] = pronunciation
                        self.pron_to_chars[pronunciation].add(char)
                    # Сохраняем омофоны: все иероглифы из этой строки для каждого иероглифа
                    # Омофоны есть только если в строке больше одного иероглифа
                    if len(characters) > 1:
                        for char in characters:
                            for other_char in characters:
                                if other_char != char:
                                    self.char_homophones[char].add(other_char)
                
                # Обрабатываем слова
                # ВАЖНО: омофоны определяются ТОЛЬКО из полей иероглифов (characters),
                # а не из слов! Слова могут содержать другие иероглифы, которые не являются омофонами.
                for words_str in words_lists:
                    words = [w.strip() for w in words_str.split(',') if w.strip()]
                    for word in words:
                        # Находим иероглифы слова, которые есть в списке characters (омофонов этой строки)
                        # Это важно: мы связываем слово только с теми иероглифами, которые явно указаны
                        # в полях иероглифов этой строки, а не со всеми иероглифами, которые встречаются в слове
                        word_chars = []
                        for char in characters:
                            if char in word:
                                word_chars.append(char)
                        
                        # Если нет иероглифов из этой строки в слове, пропускаем
                        if not word_chars:
                            continue
                        
                        # Отмечаем слово как обработанное только при первом добавлении
                        is_new_word = word not in self.seen_words
                        if is_new_word:
                            self.seen_words.add(word)
                        
                        # Сохраняем данные слова
                        if word not in self.words_data:
                            self.words_data[word] = {
                                'pronunciation': pronunciation,
                                'characters': word_chars.copy(),
                                'all_characters': characters.copy()
                            }
                        else:
                            # Если слово уже существует, добавляем новые иероглифы к существующему списку
                            # Это важно для слов, которые встречаются в нескольких строках
                            # Например, слово "分钟" встречается и в строке с "分", и в строке с "钟"
                            existing_chars = set(self.words_data[word]['characters'])
                            for char in word_chars:
                                if char not in existing_chars:
                                    self.words_data[word]['characters'].append(char)
                            # Также обновляем произношение, если оно было пустым
                            if not self.words_data[word].get('pronunciation'):
                                self.words_data[word]['pronunciation'] = pronunciation
                        
                        # Сохраняем связь иероглиф -> слова
                        # Только для иероглифов, которые есть в characters (полях иероглифов)
                        for char in word_chars:
                            self.char_to_words[char].add(word)
    
    def parse_second_csv(self, filepath: str):
        """
        Парсит второй CSV файл с переводами.
        Формат: иероглиф;произношение;перевод (тип: значение | тип: значение)
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            # Определяем разделитель автоматически
            first_line = f.readline()
            f.seek(0)
            delimiter = ';' if ';' in first_line else ','
            reader = csv.reader(f, delimiter=delimiter)
            for row in reader:
                if len(row) < 3:
                    continue
                
                word = row[0].strip()
                pronunciation = row[1].strip()
                translation_str = row[2].strip()
                
                if not word or not translation_str:
                    continue
                
                # Парсим переводы по типам
                translations = self._parse_translations(translation_str)
                
                # Обновляем данные слова
                # ВАЖНО: произношение из второго CSV имеет приоритет, так как там указано произношение всего слова
                if word not in self.words_data:
                    self.words_data[word] = {
                        'pronunciation': pronunciation,
                        'characters': list(word),
                        'all_characters': []
                    }
                else:
                    # Всегда обновляем произношение из второго CSV, так как там произношение всего слова
                    self.words_data[word]['pronunciation'] = pronunciation
                
                self.words_data[word]['translations'] = translations
                
                # Сохраняем произношение для иероглифов
                # НО не добавляем омофоны из второго CSV, так как там нет информации о том,
                # какие иероглифы являются омофонами (омофоны определяются только из первого CSV)
                for char in word:
                    if char not in self.pronunciations:
                        self.pronunciations[char] = pronunciation
                    self.pron_to_chars[pronunciation].add(char)
                    self.char_to_words[char].add(word)
    
    def _parse_translations(self, translation_str: str) -> Dict[str, List[str]]:
        """
        Парсит строку переводов в словарь по типам.
        Формат: "тип1: значение1, значение2 | тип2: значение3"
        """
        translations = defaultdict(list)
        
        # Разделяем по |
        parts = [p.strip() for p in translation_str.split('|')]
        
        for part in parts:
            if ':' in part:
                type_part, meaning = part.split(':', 1)
                word_type = type_part.strip()
                meaning = meaning.strip()
                
                if word_type and meaning:
                    # Разделяем значения по запятой
                    meanings = [m.strip() for m in meaning.split(',') if m.strip()]
                    translations[word_type].extend(meanings)
        
        return dict(translations)
    
    def get_word_data(self, word: str) -> Dict:
        """Возвращает данные для слова."""
        return self.words_data.get(word, {})
    
    def get_all_words(self) -> List[str]:
        """Возвращает список всех уникальных слов."""
        return list(self.words_data.keys())
    
    def get_char_analysis(self, char: str) -> Dict:
        """
        Возвращает разбор иероглифа:
        - слова с таким же иероглифом
        - иероглифы с идентичным звучанием (омофоны из первого CSV)
        """
        words_with_char = list(self.char_to_words.get(char, set()))
        # Используем сохраненные омофоны из первого CSV (иероглифы из той же строки)
        homophones = list(self.char_homophones.get(char, set()))
        
        return {
            'words': words_with_char,
            'chars_with_same_pronunciation': homophones
        }
