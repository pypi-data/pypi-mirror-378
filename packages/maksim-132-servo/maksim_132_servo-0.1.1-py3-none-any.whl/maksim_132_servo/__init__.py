"""
Библиотека maksim_132_servo для управления сервомотором через Arduino
Автор: Максим Рогов
"""

from .main import ServoController, TelegramServoBot
import threading

# Глобальные экземпляры
_servo_instance = None
_bot_instance = None
_bot_thread = None

def init(port='COM4', baudrate=9600):
    """
    Инициализация соединения с Arduino
    """
    global _servo_instance
    _servo_instance = ServoController(port, baudrate)
    return _servo_instance

def servo(angle):
    """
    Поворот сервомотора на указанный угол
    """
    global _servo_instance
    if _servo_instance is None:
        _servo_instance = ServoController()
    
    success = _servo_instance.set_angle(angle)
    if success:
        return f"Сервомотор повернут на {angle}°"
    else:
        return f"Ошибка поворота на {angle}°"

def sweep(start=0, end=180, step=10, delay=0.3):
    """
    Плавное движение сервомотора между углами
    """
    global _servo_instance
    if _servo_instance is None:
        _servo_instance = ServoController()
    
    _servo_instance.sweep(start, end, step, delay)

def bot(token, port='COM4'):
    """
    Запуск Telegram бота для управления сервомотором
    """
    global _servo_instance, _bot_instance, _bot_thread
    
    if _servo_instance is None:
        _servo_instance = ServoController(port)
    
    _bot_instance = TelegramServoBot(token, _servo_instance)
    
    # Запуск бота в отдельном потоке
    def run_bot():
        _bot_instance.run()
    
    _bot_thread = threading.Thread(target=run_bot, daemon=True)
    _bot_thread.start()
    
    return "Telegram бот запущен в фоновом режиме"

def cleanup():
    """Закрытие соединения с Arduino"""
    global _servo_instance, _bot_instance
    if _servo_instance:
        _servo_instance.close()
    _servo_instance = None
    _bot_instance = None

# Явный экспорт
__all__ = ['ServoController', 'TelegramServoBot', 'init', 'servo', 'sweep', 'bot', 'cleanup']