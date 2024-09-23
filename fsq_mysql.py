import requests
import pandas as pd
import mysql.connector
from mysql.connector import Error
import configparser

# Загрузка конфигурации
config = configparser.ConfigParser()
config.read('B:/GB/fsq/config.ini')

# Получение API ключей из конфигурации

access_api = config['api']['access_api']
db_host = config['database']['host']
db_port = config['database']['port']
db_database = config['database']['dbase']
db_user = config['database']['user']
db_password = config['database']['password']

VERSION = '20240922'  # Текущая дата в формате YYYYMMDD

def check_authorization():
    url = "https://api.foursquare.com/v3/places/search"
    headers = {
        'Authorization': access_api,
    }
    response = requests.get(url, headers=headers, params={'near': 'Москва', 'limit': 1})
    
    if response.status_code == 401:
        print("Ошибка авторизации: неверный токен доступа.")
        return False
    elif response.status_code != 200:
        print("Ошибка при проверке авторизации:", response.json().get('message', 'Неизвестная ошибка'))
        return False
    return True

def search_places(category):
    url = "https://api.foursquare.com/v3/places/search"
    headers = {
        'Authorization': access_api,
    }
    params = {
        'near': 'Москва',  # Вы можете изменить на нужный вам город
        'query': category,
        'limit': 50  # Ограничение на количество результатов
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        venues = response.json().get('results', [])
        if venues:
            data = []
            for venue in venues:
                name = venue['name']
                address = venue.get('location', {}).get('formatted_address', 'Нет адреса')
                rating = venue.get('rating', None)
                
                if rating is not None and isinstance(rating, (int, float)):
                    rating = float(rating)  # Приведение к типу float
                else:
                    rating = None  # Или установите значение по умолчанию

                data.append({'Название': name, 'Адрес': address, 'Рейтинг': rating})
            save_to_csv(data, category)
            save_to_mysql(data, category)
        else:
            print("Заведения не найдены.")
    else:
        print("Ошибка при получении данных:", response.json().get('message', 'Неизвестная ошибка'))

def save_to_csv(data, category):
    df = pd.DataFrame(data)
    df.to_csv(f'{category}.csv', index=False, encoding='utf-8-sig')
    print("Данные сохранены в файл " + category + ".csv")

def save_to_mysql(data, category):
    connection = None  # Initialize connection variable
    try:
        connection = mysql.connector.connect(
            host=db_host,  # Corrected: no port here
            port=db_port,  # Specify the port separately
            database=db_database,  # Замените на ваше имя базы данных
            user=db_user,  # Замените на ваше имя пользователя
            password=db_password  # Замените на ваш пароль
        )
        
        cursor = connection.cursor()
        # Создание таблицы, если она не существует
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS `{}` (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                address VARCHAR(255),
                rating FLOAT
            )
        '''.format(category))
        
        # Вставка данных в таблицу
        for venue in data:
            cursor.execute('''
                INSERT INTO `{}` (name, address, rating) 
                VALUES (%s, %s, %s)
            '''.format(category), (venue['Название'], venue['Адрес'], venue['Рейтинг']))
        
        connection.commit()
        print("Данные успешно добавлены в таблицу '" + category + "'")
        
    except Error as e:
        print("Ошибка при работе с MySQL:", e)
    finally:
        if connection is not None and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    if check_authorization():
        category = input("Введите категорию (например, кофейни, музеи, парки и т.д.): ")
        search_places(category)