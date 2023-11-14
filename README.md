# praktikum_new_diplom
Для развертывания backend-проекта на локальном ПК необходимо:
1) Развернуть виртуальное окружение
    - python -m venv venv
    - source venv/Scripts/activate
2) Установить зависимости из директории backend/
    - pip install -r requirements.txt
3) Выполнить миграции
    - python manage.py migrate
4) Наполнить базу данных тестовыми данными
    - python manage.py load_test_data
5) Запустить проект
    - python manage.py runserver

URL, отсутствующий в документации, но требуемый по ТЗ:
    api/recipes/favorites/ - передает страницу со всеми избранными рецептами