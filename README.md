# hw05_final

[![CI](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml)

<h2 align="center">Проект Yatube</h2>
<h4>Проект Yatube - это социальная сеть, основная функция которой - публикация постов - по сути, соцсеть для ведения блога, который могут комментировать другие люди.</h4>

<h2>Установка:</h2>

1) Клонируйте репозиторий и перейдите в папку проекта:

```
git clone git@github.com:DayKotya/hw05_final.git
```

```
cd api_final_yatube
```

2) Cоздайте и активируйте виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

3) Установите зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

4) Выполните миграции:

```
python3 manage.py migrate
```

5) Запустите проект:

```
python3 manage.py runserver
```

<h2>Использованные технологии:</h2>

<ul>
<li><p>Python 3.7.9</p></li>
<li><p>Django 2.2.16</p></li>
</ul>
