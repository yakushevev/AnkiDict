# Инструкция по публикации проекта на GitHub

## Шаг 1: Создайте репозиторий на GitHub

1. Перейдите на https://github.com/new
2. Заполните форму:
   - **Repository name**: `ankiDict` (или другое имя на ваш выбор)
   - **Description**: `Генератор словарей Anki из CSV файлов с поддержкой TTS`
   - Выберите **Public** или **Private**
   - **НЕ** создавайте README, .gitignore или лицензию (они уже есть в проекте)
3. Нажмите **Create repository**

## Шаг 2: Подключите локальный репозиторий к GitHub

После создания репозитория GitHub покажет вам команды. Выполните их в терминале:

```bash
# Добавьте remote (замените YOUR_USERNAME на ваш GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/ankiDict.git

# Переименуйте ветку в main (если нужно)
git branch -M main

# Отправьте код на GitHub
git push -u origin main
```

## Альтернативный способ (через SSH)

Если вы используете SSH ключи:

```bash
git remote add origin git@github.com:YOUR_USERNAME/ankiDict.git
git branch -M main
git push -u origin main
```

## Готово!

После выполнения команд ваш проект будет доступен на GitHub по адресу:
`https://github.com/YOUR_USERNAME/ankiDict`
