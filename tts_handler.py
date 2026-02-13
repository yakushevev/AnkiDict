"""
Модуль для генерации озвучки слов с помощью TTS.
"""
import os
from pathlib import Path
from gtts import gTTS
import hashlib
import threading
import time

class TTSHandler:
    """Класс для обработки TTS (Text-to-Speech)."""
    
    def __init__(self, audio_dir: str = "audio_cache", lang: str = "zh"):
        """
        Инициализация TTS обработчика.
        
        Args:
            audio_dir: Директория для кэширования аудио файлов
            lang: Язык для TTS (zh - китайский)
        """
        self.audio_dir = Path(audio_dir)
        self.lang = lang
        self.audio_dir.mkdir(exist_ok=True)
    
    def get_audio_path(self, text: str) -> str:
        #return ""
        """
        Генерирует или возвращает путь к аудио файлу для текста.
        
        Args:
            text: Текст для озвучки
            
        Returns:
            Путь к аудио файлу
        """
        # Создаем уникальное имя файла на основе текста
        hash_name = hashlib.md5(text.encode('utf-8')).hexdigest()
        audio_path = self.audio_dir / f"{hash_name}.mp3"
        
        # Если файл уже существует, возвращаем его
        if audio_path.exists():
            return str(audio_path)
        
        # Генерируем новый аудио файл
        try:
            # Создаем событие для синхронизации
            completion_event = threading.Event()
            generation_error = None
            
            def generate_audio():
                nonlocal generation_error
                try:
                    tts = gTTS(text=text, lang=self.lang, slow=False)
                    tts.save(str(audio_path))
                except Exception as e:
                    generation_error = e
                finally:
                    completion_event.set()
            
            # Запускаем генерацию в отдельном потоке
            thread = threading.Thread(target=generate_audio)
            thread.daemon = True
            thread.start()
            
            # Ожидаем завершения с таймаутом 3 секунды
            if completion_event.wait(timeout=3.0):
                if generation_error:
                    raise generation_error
                return str(audio_path)
            else:
                # Таймаут превышен
                print(f"Таймаут при генерации аудио для '{text}': превышено время ожидания 3 секунды")
                return ""
        except Exception as e:
            print(f"Ошибка при генерации аудио для '{text}': {e}")
            return ""
    
    def cleanup(self):
        """Очищает кэш аудио файлов (опционально)."""
        # Можно добавить логику очистки старых файлов
        pass
