# Установка

## Проблема: Python 3.11 не найден

```bash
$ make install-dev
❌ ERROR: Python 3.11 not found!
```

## Решение

### Ubuntu/Kubuntu

```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev

# Проверка
python3.11 --version

# Теперь
make install-dev
```

## Почему 3.11?

- ✅ Stability (LTS)
- ✅ All libraries tested
- ✅ Production standard
- ⚠️ 3.13 too new

## Ruff vs Black

**Ruff заменяет:**
- Black (formatter)
- Flake8 (linter)
- isort (import sorting)

**Преимущества:**
- 10-100x быстрее
- Один инструмент вместо 3х
- Совместим с Black

Поэтому **убрал Black** из проекта.
