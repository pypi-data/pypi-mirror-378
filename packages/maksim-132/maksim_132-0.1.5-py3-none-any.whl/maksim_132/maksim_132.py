import requests
import json
import logging
from typing import Optional, Dict, Any

class Maksim132:
    def __init__(self):
        self.bot_token = None
        self.chat_id = None
        self.base_url = None
        
    def located(self, bot_token: str, chat_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Определяет местоположение и отправляет в Telegram бота
        
        Args:
            bot_token (str): Токен Telegram бота
            chat_id (str, optional): ID чата для отправки (если не указан, будет использован ID из getUpdates)
        
        Returns:
            dict: Информация о местоположении
        """
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
        # Получаем информацию о местоположении
        location_data = self._get_location()
        
        if not location_data:
            return {"error": "Не удалось определить местоположение"}
        
        # Если chat_id не указан, пытаемся получить его из обновлений
        if not chat_id:
            chat_id = self._get_chat_id()
            
        if not chat_id:
            return {"error": "Не указан chat_id и не удалось его получить автоматически"}
        
        self.chat_id = chat_id
        
        # Отправляем местоположение в Telegram
        success = self._send_location_to_telegram(location_data)
        
        if success:
            location_data["status"] = "Местоположение отправлено в Telegram"
        else:
            location_data["status"] = "Ошибка отправки в Telegram"
            
        return location_data
    
    def _get_location(self) -> Optional[Dict[str, Any]]:
        """Получает информацию о местоположении через IP API"""
        try:
            response = requests.get('http://ip-api.com/json/', timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'success':
                return {
                    'ip': data.get('query', ''),
                    'country': data.get('country', ''),
                    'region': data.get('regionName', ''),
                    'city': data.get('city', ''),
                    'zip': data.get('zip', ''),
                    'lat': data.get('lat', ''),
                    'lon': data.get('lon', ''),
                    'isp': data.get('isp', ''),
                    'org': data.get('org', ''),
                    'as': data.get('as', '')
                }
            else:
                return None
                
        except requests.RequestException as e:
            logging.error(f"Ошибка получения местоположения: {e}")
            return None
    
    def _get_chat_id(self) -> Optional[str]:
        """Получает chat_id из последнего сообщения боту"""
        try:
            response = requests.get(f"{self.base_url}/getUpdates", timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data['ok'] and data['result']:
                # Берем chat_id из последнего сообщения
                last_update = data['result'][-1]
                if 'message' in last_update:
                    return str(last_update['message']['chat']['id'])
                elif 'callback_query' in last_update:
                    return str(last_update['callback_query']['message']['chat']['id'])
                    
            return None
            
        except requests.RequestException as e:
            logging.error(f"Ошибка получения chat_id: {e}")
            return None
    
    def _send_location_to_telegram(self, location_data: Dict[str, Any]) -> bool:
        """Отправляет местоположение в Telegram"""
        try:
            # Формируем текст сообщения
            message = f"📍 Обнаружено местоположение:\n\n"
            message += f"🌍 Страна: {location_data.get('country', 'Неизвестно')}\n"
            message += f"🏙 Регион: {location_data.get('region', 'Неизвестно')}\n"
            message += f"🏢 Город: {location_data.get('city', 'Неизвестно')}\n"
            message += f"📮 ZIP: {location_data.get('zip', 'Неизвестно')}\n"
            message += f"📡 IP: {location_data.get('ip', 'Неизвестно')}\n"
            message += f"📍 Координаты: {location_data.get('lat', '')}, {location_data.get('lon', '')}\n"
            message += f"📶 Провайдер: {location_data.get('isp', 'Неизвестно')}\n"
            message += f"🏢 Организация: {location_data.get('org', 'Неизвестно')}"
            
            # Отправляем текстовое сообщение
            text_payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(
                f"{self.base_url}/sendMessage",
                json=text_payload,
                timeout=10
            )
            
            # Если есть координаты, отправляем также location
            if location_data.get('lat') and location_data.get('lon'):
                location_payload = {
                    'chat_id': self.chat_id,
                    'latitude': location_data['lat'],
                    'longitude': location_data['lon']
                }
                
                requests.post(
                    f"{self.base_url}/sendLocation",
                    json=location_payload,
                    timeout=10
                )
            
            return response.status_code == 200
            
        except requests.RequestException as e:
            logging.error(f"Ошибка отправки в Telegram: {e}")
            return False

# Создаем экземпляр для импорта
maksim_132 = Maksim132()