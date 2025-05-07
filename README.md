# File-Structuring-System

## Опис проєкту
Інформаційна система структурування файлів сховища даних - це проєкт, розроблений як частина бакалаврської кваліфікаційної роботи. Система призначена для ефективного управління та організації файлової структури у сховищах даних.

## Технології
- **Backend**: FastAPI (Python)
- **Frontend**: Vite + React
- **Розгортання**: Docker (опціонально)

## Встановлення та запуск

### Вимоги
- Python 3.8+
- Node.js 16+
- npm

### Локальний запуск

1. Клонуйте репозиторій:
```bash
git clone https://github.com/your-username/File-Structuring-System.git
cd File-Structuring-System
```

2. Запустіть систему в режимі розробки:
```bash
python run.py -c config.json
```

3. Для продакшен режиму:
```bash
python run.py -c config.json -p
```

## Структура проєкту
```
File-Structuring-System/
├── backend/
│   ├── app/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   └── package.json
├── run.py
└── README.md
```

## Ліцензія
MIT License

## Inspiration
- [iyaja/llama-fs](https://github.com/iyaja/llama-fs)
- [drforse/not-llama-fs](https://github.com/drforse/not-llama-fs)