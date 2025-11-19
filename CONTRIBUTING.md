# Руководство по вкладу

## Начало работы

1. **Fork репозитория**
2. **Клонировать ваш fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/preparing.git
   cd preparing
   ```

3. **Создать ветку для фичи**
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Установить зависимости для разработки**
   ```bash
   make install-dev
   pre-commit install
   ```

## Стандарты кода

### Python

- **Форматирование**: Black (88 символов)
- **Импорты**: isort с profile=black
- **Типы**: mypy --strict
- **Linting**: flake8
- **Docstrings**: Google style

### Пример docstring

```python
def my_function(param1: str, param2: int) -> bool:
    """Brief description.

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When something goes wrong
    """
    pass
```

## Процесс разработки

1. **Написать код**
2. **Запустить форматирование**
   ```bash
   make format
   ```

3. **Запустить linting**
   ```bash
   make lint
   ```

4. **Написать тесты**
   - Каждая новая функция должна иметь тесты
   - Цель: 80%+ coverage

5. **Запустить тесты**
   ```bash
   make test
   ```

6. **Commit изменений**
   ```bash
   git add .
   git commit -m "feat: Add feature description"
   ```

   **Commit сообщения:**
   - `feat:` - новая функциональность
   - `fix:` - исправление бага
   - `docs:` - документация
   - `test:` - тесты
   - `refactor:` - рефакторинг
   - `chore:` - технические задачи

7. **Создать Pull Request**
   - Опишите изменения
   - Ссылка на issue (если есть)
   - Дождитесь review

## CI/CD

GitHub Actions автоматически:
- Запустит все тесты
- Проверит качество кода
- Сгенерирует coverage report

PR не будет смержен, если:
- Тесты не проходят
- Linting ошибки
- Coverage < 80%

## Вопросы

Создайте issue или напишите в discussions.
