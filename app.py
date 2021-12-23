from flask import Flask, Response, render_template
from flask.json import dumps

import pandas as pd
import numpy as np

app = Flask(__name__)
app.secret_key = b'11111111111111111'

#Задача 1
def _spending(file_name) -> pd.DataFrame:
    # Читаем файл эксель
    df: pd.DataFrame = pd.read_excel(file_name)
    # Добавляем столбец с итоговыми данными 
    df['Затраты'] = df['Количество'] * df['Цена']
    # Создаем уникальный "id" (key) для Реакта, за остуствием такового в исходном файле
    df['key'] = df.index
    # Итоговая строка будет сгенерирована позже, т.к. в реакт пойдут "чистые" данные
    return df

#Задача 2
def _spending_by_mnn(file_name) -> pd.DataFrame:
    # Первые 2 шага аналогичны Задаче 1
    df: pd.DataFrame = pd.read_excel(file_name)
    df['Затраты'] = df['Количество'] * df['Цена']
    # Группируем по МНН и агрегируем через лямбда функцию, возращающую Серию.
    # Далее все соберем в новый Фрейм
    grp: pd.DataFrame = df.groupby('Международное непатентованное наименование').apply(lambda x: pd.Series({
        'Торговое наименование': '\n'.join(x['Торговое наименование']), #склеиваем: разделитель – перенос строки
        'Форма выпуска': '\n'.join(x['Форма выпуска']), # - // -
        'Количество': x['Количество'].sum(), # суммируем весь столбец
        'Цена': np.average(x['Цена'], weights=x['Количество']), # вычисляем среднее взвешенное 
        'Затраты': x['Затраты'].sum() 
        }))
    # Возвращаем индекс "МНН" обратно колонку, на фоне генерируется новый индекс
    grp.reset_index(inplace=True)
    # Создаем уникальный "id" для использования в Реакте
    grp['key'] = grp.index
    return grp

# Задача 3
def _medicine() -> dict:
    # готовим SQL запрос
    stmt = '''
    SELECT 
        mnn.id mnn_id,
        mnn.MNN mnn,
        tn.TN tn,
        mnn.VEN ven
    FROM spTN tn
	    LEFT JOIN spMNN mnn ON tn.MNN = mnn.id
    '''
    # Загружаем информацию из базы sqlite по запросу сразу во Фрейм.
    # За кулисами работает sqlalchemy со всеми необходимыми драйверами
    df = pd.read_sql_query(stmt, con='sqlite:///test_data.db')
    # Чистим столбец ТН от лишних пробелов и переносов строк
    df['tn'] = df['tn'].str.strip()
    # Группируем по МНН и аггрегируем в Серию
    grp = df.groupby('mnn').apply(lambda x: pd.Series({
        'key': x['mnn_id'].iloc[0], # Забираем первый попавшийся mnn.id в качестве ключа - они все одинаковые 
        'tn': '\n'.join(x['tn']),  # Склеиваем в одну строку
        'ven': x['ven'].iloc[0] == 1 # Переводим ven в boolean для дальнейшего использования
    }))
    # Возвращаем индекс в колонку Фрейма
    grp.reset_index(inplace=True)
    # Сотрирум по признаку ЖВНЛП, затем по МНН и сохраняем состояние текущего Фрейма
    grp.sort_values(['ven','mnn'], ascending=[False,True], inplace=True)
    # Используем колонку ЖВНЛП в качестве маски для фильтрации Фрейма
    is_ven = grp['ven']
    return {
        # Отфильтровываем Фрейм по признаку ЖВНЛП и преобразуем в словарь вида {0:{tn:имя_тн, mnn:имя_мнн}, 1:{...}}
        # Далее оставляем только значения и преобразуем в список вида [{tn:имя_тн, mnn:имя_мнн}, {...}] для последующей сериализации в json
        'ven': list(grp[is_ven].to_dict(orient='index').values()),
        # Тут отфильтровываем по обратному признаку
        'other': list(grp[~is_ven].to_dict(orient='index').values())
    }

# shortcut для сериализации ответа
def json_response(data:dict):
    return Response(response=dumps(data, ensure_ascii=False), status=200, mimetype='application/json')

# Далее идут непосредственно обработчики запросов веб-сервера/приложения Flask, как в классическом варианте с шаблонизатором, так и в варианте первого уровня rest

@app.route('/')
def index():
    # Рендерим шаблон из папки templates
    # Все шаблоны наследуются от base.html и преопределяют его блок container. По-необходимости включаем блок меню (nav.html) 
    return render_template('index.html')

@app.route('/react')
def react():
    # В шаблоне включаем библиотеки Реакта перед закрывающим тегом </body>
    # Библиотеки все "со стороны". Остался только один локальный файл - static/app.js, но и его можно поместить в шаблон
    return render_template('react.html')

# Обработка запроса к задаче 1
@app.route('/spending')
def spending():
    # Основные моменты описаны выше, в функции _spending()
    df = _spending('test_data.xlsx')
    # Добавляем строку с итоговыми суммами по задаче 1
    df.loc['Сумма',['Количество','Цена','Затраты']] = df[['Количество','Цена','Затраты']].sum()
    # Избавляемся от np.NaN в наименованиях
    # В идеале лучше бы убрать длинные наименования колонок, но с другой стороны их можно использовать для генерации нового эксель файла.
    df.loc['Сумма',['Международное непатентованное наименование','Торговое наименование','Форма выпуска']] = ''
    # Преобразуем Фрейм в словарь и отбрасываем ключи. 
    # Приводить к списку не имеет смысла, т.к. сериализации в json не будет, а циклу хватит и "генератора"
    data = df.to_dict(orient='index').values()
    return render_template('spending.html', rows=data)

# Все тоже самое, но в виде ответа json и без итоговой суммы - пускай на клиенте считает
@app.route('/api/spending')
def spending_api():
    df = _spending('test_data.xlsx')
    # Тут нужно обернуть ответ в список, иначе не сериализуется в json
    data = list(df.to_dict(orient='index').values())
    return json_response({'data':data})

# Обработка запроса к задаче 2
@app.route('/spending_by_mnn')
def spending_by_mnn():
    # Вся логика описана в функции _spending_by_mnn(), а хвост ничем не отличается от задачи 1
    # можно вынести в отдельную функцию 
    df = _spending_by_mnn('test_data.xlsx')
    df.loc['Сумма',['Количество','Цена','Затраты']] = df[['Количество','Цена','Затраты']].sum()
    df.loc['Сумма',['Международное непатентованное наименование','Торговое наименование','Форма выпуска']] = ''
    data = df.to_dict(orient='index').values()
    return render_template('spending.html', rows=data)

# Тоже самое в json
@app.route('/api/spending_by_mnn')
def spending_by_mnn_api():
    df = _spending_by_mnn('test_data.xlsx')
    data = list(df.to_dict(orient='index').values())
    return json_response({'data':data})

# Обработка запроса к задаче 3, все аналогично
@app.route('/medicine')
def medicine():
    data = _medicine()
    return render_template('medicine.html', ven=data['ven'], other=data['other'])

@app.route('/api/medicine')
def medicine_api():
    data = _medicine()
    return json_response({'data':data})
