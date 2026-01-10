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
            reader = csv.reader(f, delimiter=';')
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
                for char in characters:
                    self.pronunciations[char] = pronunciation
                    self.pron_to_chars[pronunciation].add(char)
                    # Сохраняем омофоны: все иероглифы из этой строки для каждого иероглифа
                    for other_char in characters:
                        if other_char != char:
                            self.char_homophones[char].add(other_char)
                
                # Обрабатываем слова
                for words_str in words_lists:
                    words = [w.strip() for w in words_str.split(',') if w.strip()]
                    for word in words:
                        if word not in self.seen_words:
                            self.seen_words.add(word)
                            
                            # Находим иероглифы слова
                            word_chars = []
                            for char in characters:
                                if char in word:
                                    word_chars.append(char)
                            
                            # Сохраняем данные слова
                            if word not in self.words_data:
                                self.words_data[word] = {
                                    'pronunciation': pronunciation,
                                    'characters': word_chars,
                                    'all_characters': characters.copy()
                                }
                            
                            # Сохраняем связь иероглиф -> слова
                            for char in word_chars:
                                self.char_to_words[char].add(word)
    
    def parse_second_csv(self, filepath: str):
        """
        Парсит второй CSV файл с переводами.
        Формат: иероглиф;произношение;перевод (тип: значение | тип: значение)
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
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
                if word not in self.words_data:
                    self.words_data[word] = {
                        'pronunciation': pronunciation,
                        'characters': list(word),
                        'all_characters': []
                    }
                else:
                    # Обновляем произношение если нужно
                    if not self.words_data[word].get('pronunciation'):
                        self.words_data[word]['pronunciation'] = pronunciation
                
                self.words_data[word]['translations'] = translations
                
                # Сохраняем произношение для иероглифов
                for char in word:
                    if char not in self.pronunciations:
                        self.pronunciations[char] = pronunciation
                    self.pron_to_chars[pronunciation].add(char)
                    self.char_to_words[char].add(word)
                    # Добавляем омофоны: все иероглифы с таким же произношением
                    chars_with_same_pron = self.pron_to_chars.get(pronunciation, set())
                    for other_char in chars_with_same_pron:
                        if other_char != char:
                            self.char_homophones[char].add(other_char)
                            self.char_homophones[other_char].add(char)
    
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
