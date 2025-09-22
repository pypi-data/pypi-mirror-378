import re
from ..forall import *
# Импорт модулей и списков функций из соответствующих подпакетов
from .mtx import *
from .fls import *

# Словарь, сопоставляющий названия тем со списками функций
files_dict ={
    'Задания с матрицами' : MTX,
    'Задания с файлами': FLS
    
}


# Получение списков названий тем и соответствующих модулей (списков функций)
names = list(files_dict.keys())
modules = list(files_dict.values())

# Создание словарей функций для каждой темы
# funcs_dicts: {описание_задачи: функция}
funcs_dicts = [dict([(get_task_from_func(i), i) for i in module]) for module in modules]
# funcs_dicts_ts: {описание_задачи_без_пробелов_и_переносов: функция} (ts - to_search)
funcs_dicts_ts = [dict([(get_task_from_func(i,True), i) for i in module]) for module in modules]
# funcs_dicts_full: {имя_функции: исходный_код_функции}
funcs_dicts_full = [dict([(i.__name__, getsource(i)) for i in module]) for module in modules]
# funcs_dicts_full_nd: {имя_функции: исходный_код_функции_без_документации}
funcs_dicts_full_nd = [dict([(i.__name__, getsource_no_docstring(i)) for i in module]) for module in modules]

# Создание словарей, группирующих функции по темам
themes_list_funcs = dict([(names[i],list(funcs_dicts[i].values()) ) for i in range(len(names))])        # Название темы : список функций по теме
themes_list_dicts = dict([(names[i],funcs_dicts[i]) for i in range(len(names))])                        # Название темы : словарь по теме, где ЗАДАНИЕ: ФУНКЦИИ
themes_list_dicts_full = dict([(names[i],funcs_dicts_full[i]) for i in range(len(names))])              # Название темы : словарь по теме, где НАЗВАНИЕ ФУНКЦИИ: ТЕКСТ ФУНКЦИИ
themes_list_dicts_full_nd = dict([(names[i],funcs_dicts_full_nd[i]) for i in range(len(names))])        # Название темы : словарь по теме, где НАЗВАНИЕ ФУНКЦИИ: ТЕКСТ ФУНКЦИИ БЕЗ ДОКУМЕНТАЦИИ



def description(
    dict_to_show=themes_list_funcs,
    key=None,
    show_only_keys: bool = False,
    show_keys_second_level: bool = True,
    n_symbols: int = 32,
    to_print: bool = True,
    show_doc = False):
    """
    Форматированный вывод информации о функциях и заданиях из словарей тем.

    Parameters
    ----------
    dict_to_show : str or dict, optional
        Имя словаря тем или сам словарь вида {функция: задание}.
        По умолчанию используется `themes_list_funcs`.
    key : hashable, optional
        Ключ для фильтрации конкретного элемента словаря.
    show_only_keys : bool, optional
        Если True - показывать только ключи словаря.
    show_keys_second_level : bool, optional
        Если True - показывать ключи второго уровня (названия функций).
    n_symbols : int, optional
        Максимальное количество символов описания для отображения.
    to_print : bool, optional
        Если True - выводить результат через print(), иначе вернуть как строку.
    show_doc : bool, optional
        Если True - выводить результат поиска функции по теме и названию вместе с ее докстрингом. Иначе без.
    Returns
    -------
    str or None
        Форматированная строка с информацией (если to_print=False).
        При to_print=True возвращает None, выводя результат напрямую.

    Notes
    -----
    1. Функция поддерживает два режима работы:
       - При передаче строки в dict_to_show: использует предопределенные словари тем
       - При передаче словаря напрямую: работает с пользовательскими структурами
    2. Использует вспомогательную функцию invert_dict() для преобразования словарей.
    3. При обработке описаний автоматически добавляется перенос строк для длинных текстов.
    4. В случае ошибок при извлечении описаний (например, отсутствующий ключ) - пропускает проблемные элементы.

    Examples
    --------
    >>> description('math_operations', show_only_keys=True)
    Сложение  : 
    Вычитание : 
    Умножение : 

    >>> description('data_processing', n_symbols=50)
    clean_data   : Очистка данных от пропусков...
    analyze_data : Проведение статистического анализа...

    >>> description('api_calls', key='get_request')
    get_request : Выполняет GET-запрос к API с параметрами...

    References
    ----------
    .. [1] Python Software Foundation. "Python Language Reference", version 3.11.
    .. [2] Beazley, D.M. "Python Essential Reference", 4th edition.
    .. [3] Ramalho, L. "Fluent Python: Clear, Concise, and Effective Programming".
    """
    
    # Если dict_to_show - строка (название темы) и не указан конкретный ключ (key)
    if type(dict_to_show) == str and key == None:
        dict_to_show = themes_list_dicts[dict_to_show]
        dict_to_show = invert_dict(dict_to_show)
        text = ""
        length1 = 1 + max([len(x.__name__) for x in list(dict_to_show.keys())])
        
        for key in dict_to_show.keys():
            text += f'{key.__name__:<{length1}}' # Имя функции, выровненное по левому краю
            
            if not show_only_keys:
                text += ': '
                text += f'{dict_to_show[key]};\n' + ' '*(length1+2) # Описание задачи
            text += '\n'
            
        if to_print == True:
            return print(text)
        return text
    
    # Если dict_to_show - строка (название темы) и указан конкретный ключ (имя функции)
    elif type(dict_to_show) == str and key in themes_list_dicts_full[dict_to_show].keys():
        if show_doc:
            return print(themes_list_dicts_full[dict_to_show][key]) # Вывод исходного кода функции
        else:
            return print(themes_list_dicts_full_nd[dict_to_show][key]) # Вывод исходного кода функции
    
    else:
        show_only_keys = False
    text = ""
    length1 = 1 + max([len(x) for x in list(dict_to_show.keys())]) # Максимальная длина ключа первого уровня (названия темы)
    
    for key in dict_to_show.keys():
        text += f'{key:^{length1}}' # Название темы, выровненное по центру
        if not show_only_keys:
            text += ': '
            for f in dict_to_show[key]:
                text += f'{f.__name__}'
                if show_keys_second_level:
                    text += ': '
                    try:
                        # Получение описания функции из инвертированного словаря
                        func_text_len = len(invert_dict(themes_list_dicts[key])[f])
                        
                        # Форматирование описания с переносами строк и ограничением по длине
                        func_text = invert_dict(themes_list_dicts[key])[f]
                        text += func_text.replace('\n','\n'+' '*(length1 + len(f.__name__))) if func_text_len < n_symbols else func_text[:n_symbols].replace('\n','\n'+' '*(length1 + len(f.__name__)))+'...'
                    except:
                        pass # Пропуск, если описание не найдено
                text += ';\n' + ' '*(length1+2) # + '\n' + ' '*(length1+2)
        text += '\n'
        
    if to_print == True:
        return print(text)
    return text



def search(query: str, to_print: bool = True, data: str = description(n_symbols=10000, to_print=False)):
    """
    Выполняет поиск совпадений по запросу в структурированных данных тем и функций.

    Parameters
    ----------
    query : str
        Строка для поиска. Искать можно по части слова или фразы.
    to_print : bool, optional
        Если True - результаты выводятся через print(). По умолчанию True.
    data : str, optional
        Исходные данные для поиска в формате, возвращаемом функцией description().
        По умолчанию вызывает description(n_symbols=10000, to_print=False).

    Returns
    -------
    list or None
        При to_print=True: выводит результаты построчно через print()
        При to_print=False: возвращает список строк в формате "Тема : Описание"

    Notes
    -----
    1. Функция чувствительна к структуре входных данных:
       - Темы должны быть разделены двойными переносами строк
       - Каждая тема должна начинаться с заголовка в формате "Название_темы:"
       - Функции внутри темы должны быть в формате "имя_функции: описание"
    2. Поиск регистронезависимый
    3. Рекомендуется использовать n_symbols=10000 при вызове description() 
       для сохранения полноты описаний

    Examples
    --------
    >>> search("обработка данных")
    math_operations : Очистка данных от пропусков...
    data_processing : Обработка данных с помощью pandas...

    >>> search("ML", to_print=False)
    ['ai_tools : Машинное обучение с использованием sklearn', 
     'deep_learning : Реализация нейронных сетей']

    >>> search("API", data="custom_data_string")
    api_calls : Выполнение GET-запросов к REST API

    References
    ----------
    .. [1] Внутренняя документация проекта, описывающая структуру тем и функций
    .. [2] Python Software Foundation. "Python Language Reference", version 3.11.
    """
    # Разделение входных данных на отдельные темы
    topics = re.split(r'\n\s*\n', data)
    matches = []

    for topic_data in topics:
        # Пропуск пустых блоков тем
        if not topic_data.strip():
            continue

        topic_match = re.match(r'^\s*(.*?):', topic_data)
        if not topic_match:
            continue
        
        # Извлечение названия темы
        topic = topic_match.group(1).strip()
        # Поиск всех функций и их описаний в текущей теме
        functions = re.findall(r'(\w+)\s*:\s*([\s\S]*?)(?=\n\s*\w+\s*:|\Z)', topic_data)

        for func, description in functions:
            # Проверка наличия запроса (без учета регистра) в описании функции
            if query.lower() in description.lower():
                matches.append(f"{topic} : {description.strip()}")
    
    # Вывод результатов или их возврат списком
    if to_print:
        return print("\n".join(matches))
    return matches
