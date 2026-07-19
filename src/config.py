import os

from dotenv import load_dotenv

# Абсолютный путь к корневой папке проекта, с учётом,
# что файлы находятся в папках src, tests, data, logs
BASE_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()
# Получение имени файла с операциями из файла .env
operations_file = os.getenv("OPERATIONS_FILE_NAME")

# Путь к каталогу с файлами для тестирования (json, csv, Excel): tests\test_data
TEST_FILE_DIR = os.path.join(BASE_DIRECTORY, "tests", "test_data")
