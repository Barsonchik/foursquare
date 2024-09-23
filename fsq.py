import requests
import configparser

# Загрузка конфигурации
config = configparser.ConfigParser()
config.read('B:/GB/fsq/config.ini')

# Получение API ключей из конфигурации

access_api = config['api']['access_api']

VERSION = '20240922'  # Текущая дата в формате YYYYMMDD

def check_authorization():
    # Проверка действительности токена доступа
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
        'limit': 10  # Ограничение на количество результатов
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        venues = response.json().get('results', [])
        if venues:
            for venue in venues:
                name = venue['name']
                address = venue.get('location', {}).get('formatted_address', 'Нет адреса')
                rating = venue.get('rating', 'Нет рейтинга')
                print(f"Название: {name}, Адрес: {address}, Рейтинг: {rating}")
        else:
            print("Заведения не найдены.")
    else:
        print("Ошибка при получении данных:", response.json().get('message', 'Неизвестная ошибка'))

if __name__ == "__main__":
    if check_authorization():
        category = input("Введите категорию (например, кофейни, музеи, парки и т.д.): ")
        search_places(category)