"""
Модуль для парсинга CSV файлов с данными о словах и переводах.
"""
import csv
from typing import Dict, List, Tuple, Set
from collections import defaultdict

class CSVParser:
    """Класс для парсинга CSV файлов."""
    
    def __init__(self):
        # Словарь для хранения всех слов с их данными
        self.all_words_data: Dict[str, Dict] = {}
        
        # Словарь: произношение -> список иероглифов с этим произношением
        self.pron_to_chars: Dict[str, List[str]] = defaultdict(list)
        
        # Словарь: иероглиф -> список его произношений
        self.char_to_pron: Dict[str, List[str]] = defaultdict(list)
                
        # Словарь: иероглиф -> список слов, содержащих этот иероглиф
        self.char_to_words: Dict[str, Set[str]] = defaultdict(set)

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
                for char in characters:
                    if char not in [',', '.', '!', ';','-','?']:
                        if (pronunciation not in self.char_to_pron[char]): self.char_to_pron[char].append(pronunciation)
                        if (char not in self.pron_to_chars[pronunciation]): self.pron_to_chars[pronunciation].append(char)

                # Обрабатываем слова
                for words_str in words_lists:
                    words = [w.strip() for w in words_str.split(',') if w.strip()]
                    for word in words:
                        # Если слово еще не встречалось, добавляем его в общий список << Не обрабатывает иероглифы с разным звучанием и смыслом!!!!
                        if word not in self.all_words_data:
                            self.all_words_data[word] = {
                                'pronunciation': None,
                                'characters':  []
                            }
                            for char in list(word):
                                if char not in [',', '.', '!', ';','-','?']:
                                    if char not in self.all_words_data[word]['characters']:
                                        self.all_words_data[word]['characters'].append(char)
                        #else:
                            # Обновляем произношение, если оно было пустым
                            #if not self.all_words_data[word].get('pronunciation'):
                            #    self.all_words_data[word]['pronunciation'] = pronunciation
                            # Добавляем новые иероглифы к существующему списку
                        #    existing_chars = set(self.all_words_data[word]['characters'])
                        #    for char in characters:
                        #        if char not in existing_chars:
                        #            self.all_words_data[word]['characters'].append(char)
                        
                        # Сохраняем связь иероглиф -> слова
                        for char in list(word):
                            if word not in self.char_to_words[char]:
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
                if word not in self.all_words_data:
                    self.all_words_data[word] = {
                        'pronunciation': pronunciation,
                        'characters': list(word),
                        'translations': translations
                    }
                else:
                    # Всегда обновляем произношение из второго CSV
                    self.all_words_data[word]['pronunciation'] = pronunciation
                    self.all_words_data[word]['translations'] = translations
                
                # Сохраняем информацию о произношении для иероглифов
                #for char in word:
                #    self.char_to_pronunciations[char].append(pronunciation)
                #    self.pronunciation_to_chars[pronunciation].append(char)
                #    self.char_to_words[char].add(word)

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
        return self.all_words_data.get(word, {})

    def get_all_words(self) -> List[str]:
        """Возвращает список всех уникальных слов."""
        return list(self.all_words_data.keys())

    def get_char_analysis(self, char: str) -> Dict:
        """
        Возвращает разбор иероглифа:
        - слова с таким же иероглифом
        - иероглифы с идентичным звучанием (омофоны)
        """
        words_with_char = list(self.char_to_words.get(char, set()))
        # Используем сохраненные омофоны
        
        homophones = []
        for pron in self.char_to_pron.get(char, set()):
            for homophone in self.pron_to_chars.get(pron, set()):
                if homophone not in homophones:
                    homophones.append(homophone )
      
        return {
            'words': words_with_char,
            'chars_with_same_pronunciation': homophones
        }
