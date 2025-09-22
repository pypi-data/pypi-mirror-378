#!/usr/bin/env python3
import serial
import time
import sys
import logging
from typing import Optional, List
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

class ServoController:
    def __init__(self, port='COM3', baudrate=9600):
        """
        Контроллер сервомотора через Arduino
        Работает даже без подключения к Arduino (режим эмуляции)
        """
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.connected = False
        self.emulation_mode = False
        self.current_angle = 90  # Текущий угол для эмуляции
        
        self._connect()
    
    def _connect(self):
        """Установка соединения с Arduino или переход в режим эмуляции"""
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            
            # Даем время Arduino на инициализацию
            time.sleep(2)
            
            # Очищаем буфер
            self.ser.reset_input_buffer()
            
            self.connected = True
            self.emulation_mode = False
            print(f"✅ Подключено к Arduino на порту {self.port}")
            
        except serial.SerialException as e:
            print(f"⚠️  Arduino не найдена на порту {self.port}: {e}")
            print("🔧 Переход в режим эмуляции")
            self.connected = False
            self.emulation_mode = True
            
        except Exception as e:
            print(f"⚠️  Неожиданная ошибка: {e}")
            print("🔧 Переход в режим эмуляции")
            self.connected = False
            self.emulation_mode = True
    
    def auto_detect_port(self):
        """
        Автоматическое обнаружение порта Arduino
        Возвращает список доступных портов
        """
        available_ports = []
        
        # Список возможных портов для разных ОС
        ports_to_check = []
        if sys.platform.startswith('win'):
            ports_to_check = [f'COM{i}' for i in range(1, 21)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
            ports_to_check = [f'/dev/ttyUSB{i}' for i in range(10)] + [f'/dev/ttyACM{i}' for i in range(10)]
        
        print("🔍 Поиск доступных портов...")
        
        for port in ports_to_check:
            try:
                ser = serial.Serial(port, self.baudrate, timeout=0.1)
                ser.close()
                available_ports.append(port)
                print(f"   Найден порт: {port}")
            except (serial.SerialException, OSError):
                pass
        
        return available_ports
    
    def try_reconnect(self, port=None):
        """
        Попытка переподключения к Arduino
        """
        if port:
            self.port = port
        
        print(f"🔄 Попытка подключения к {self.port}...")
        self._connect()
        return self.connected
    
    def set_angle(self, angle):
        """
        Установка угла поворота сервомотора
        Работает в обоих режимах (реальном и эмуляции)
        """
        if angle < 0 or angle > 180:
            print("❌ Угол должен быть от 0 до 180 градусов")
            return False
        
        if self.connected and self.ser is not None:
            # Режим реального подключения
            try:
                command = f"ANGLE:{angle}\n"
                self.ser.write(command.encode('utf-8'))
                
                time.sleep(0.1)
                
                if self.ser.in_waiting > 0:
                    response = self.ser.readline().decode('utf-8').strip()
                    print(f"📨 Ответ Arduino: {response}")
                
                self.current_angle = angle
                print(f"✅ Реальный сервомотор: угол {angle}°")
                return True
                
            except serial.SerialException as e:
                print(f"❌ Ошибка связи с Arduino: {e}")
                self.connected = False
                self.emulation_mode = True
                return self.set_angle(angle)  # Рекурсивно вызываем в режиме эмуляции
                
            except Exception as e:
                print(f"❌ Неожиданная ошибка: {e}")
                return False
        
        else:
            # Режим эмуляции
            self.current_angle = angle
            print(f"🎮 Эмуляция сервомотора: угол {angle}°")
            time.sleep(0.1)  # Имитация задержки
            return True
    
    def sweep(self, start=0, end=180, step=10, delay=0.3):
        """
        Плавное движение сервомотора между углами
        Работает в обоих режимах
        """
        print(f"🔄 Плавное движение от {start}° до {end}°")
        
        # Движение вперед
        for angle in range(start, end + 1, step):
            if self.set_angle(angle):
                time.sleep(delay)
        
        # Движение назад
        for angle in range(end, start - 1, -step):
            if self.set_angle(angle):
                time.sleep(delay)
    
    def get_status(self):
        """Получение статуса подключения"""
        if self.connected:
            return f"✅ Подключено к Arduino на порту {self.port}"
        elif self.emulation_mode:
            return "🎮 Режим эмуляции (Arduino не подключена)"
        else:
            return "❌ Не подключено"
    
    def close(self):
        """Закрытие соединения"""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("🔌 Соединение с Arduino закрыто")
        self.connected = False
    
    def __del__(self):
        """Деструктор - автоматическое закрытие соединения"""
        self.close()


class TelegramServoBot:
    def __init__(self, token: str, servo_controller: ServoController):
        """
        Telegram бот для управления сервомотором
        """
        self.token = token
        self.servo = servo_controller
        self.application = Application.builder().token(token).build()
        
        # Настройка обработчиков команд
        self.setup_handlers()
        
        # Клавиатура с основными командами
        self.keyboard = ReplyKeyboardMarkup(
            [
                ["0°", "45°", "90°", "135°", "180°"],
                ["Сканировать", "Статус", "Помощь", "Поиск Arduino"]
            ],
            resize_keyboard=True
        )
    
    def setup_handlers(self):
        """Настройка обработчиков команд"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("scan", self.scan_command))
        self.application.add_handler(CommandHandler("angle", self.angle_command))
        self.application.add_handler(CommandHandler("find_arduino", self.find_arduino_command))
        self.application.add_handler(CommandHandler("reconnect", self.reconnect_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        welcome_text = f"""
        🤖 Добро пожаловать в Servo Control Bot!
        
        {self.servo.get_status()}
        
        📋 Доступные команды:
        /start - Начать работу
        /help - Показать справку
        /status - Статус подключения
        /scan - Сканировать (0°-180°-0°)
        /angle [значение] - Установить угол (0-180)
        /find_arduino - Найти Arduino автоматически
        /reconnect - Переподключиться
        
        🎮 Режим эмуляции: Бот работает даже без Arduino!
        
        Используйте кнопки ниже для быстрого управления ⬇️
        """
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=self.keyboard
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = f"""
        📖 Справка по командам:
        
        {self.servo.get_status()}
        
        Основные команды:
        /start - Начать работу с ботом
        /help - Показать эту справку
        /status - Проверить статус подключения
        /scan - Запустить сканирование (0°-180°-0°)
        /angle [значение] - Установить конкретный угол
        /find_arduino - Автопоиск Arduino
        /reconnect - Переподключиться к указанному порту
        
        🎮 Особенности:
        - Бот работает в режиме эмуляции если Arduino не найдена
        - Все команды доступны в любом режиме
        - При подключении Arduino автоматически переключается на реальное управление
        
        Примеры:
        /angle 90 - установить угол 90 градусов
        /scan - запустить автоматическое сканирование
        """
        
        await update.message.reply_text(help_text)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /status"""
        status_text = f"""
        📊 Статус системы:
        
        {self.servo.get_status()}
        Текущий угол: {self.servo.current_angle}°
        
        💡 Совет: Используйте /find_arduino для автоматического поиска
        или /reconnect COM3 для ручного подключения (замените COM3 на ваш порт)
        """
        
        await update.message.reply_text(status_text)
    
    async def scan_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /scan"""
        mode = "Реальный" if self.servo.connected else "Эмуляция"
        await update.message.reply_text(f"🔄 Запускаю сканирование ({mode} режим)...")
        
        # Запускаем сканирование в отдельном потоке
        def scan():
            self.servo.sweep()
        
        import threading
        thread = threading.Thread(target=scan)
        thread.start()
        
        await update.message.reply_text("✅ Сканирование завершено!")
    
    async def angle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /angle"""
        if not context.args:
            await update.message.reply_text("❌ Укажите угол: /angle 90")
            return
        
        try:
            angle = int(context.args[0])
            success = self.servo.set_angle(angle)
            
            mode = "Реальный" if self.servo.connected else "Эмуляция"
            if success:
                await update.message.reply_text(f"✅ Установлен угол: {angle}° ({mode} режим)")
            else:
                await update.message.reply_text("❌ Не удалось установить угол")
        except ValueError:
            await update.message.reply_text("❌ Угол должен быть числом")
    
    async def find_arduino_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /find_arduino"""
        await update.message.reply_text("🔍 Ищу Arduino на доступных портах...")
        
        available_ports = self.servo.auto_detect_port()
        
        if available_ports:
            response = "📋 Найдены порты:\n" + "\n".join([f"• {port}" for port in available_ports])
            response += f"\n\n🔄 Пробую подключиться к {available_ports[0]}..."
            
            await update.message.reply_text(response)
            
            # Пробуем подключиться к первому найденному порту
            if self.servo.try_reconnect(available_ports[0]):
                await update.message.reply_text(f"✅ Успешно подключено к {available_ports[0]}!")
            else:
                await update.message.reply_text("❌ Не удалось подключиться. Остаюсь в режиме эмуляции.")
        else:
            await update.message.reply_text("❌ Arduino не найдена. Остаюсь в режиме эмуляции.")
    
    async def reconnect_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /reconnect"""
        port = context.args[0] if context.args else self.servo.port
        
        await update.message.reply_text(f"🔄 Пробую подключиться к {port}...")
        
        if self.servo.try_reconnect(port):
            await update.message.reply_text(f"✅ Успешно подключено к {port}!")
        else:
            await update.message.reply_text(f"❌ Не удалось подключиться к {port}. Остаюсь в режиме эмуляции.")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        text = update.message.text.lower()
        
        if text == "статус":
            await self.status_command(update, context)
        elif text == "сканировать":
            await self.scan_command(update, context)
        elif text == "помощь":
            await self.help_command(update, context)
        elif text == "поиск arduino":
            await self.find_arduino_command(update, context)
        elif text.endswith("°"):
            try:
                angle = int(text.replace("°", "").strip())
                success = self.servo.set_angle(angle)
                
                mode = "Реальный" if self.servo.connected else "Эмуляция"
                if success:
                    await update.message.reply_text(f"✅ Установлен угол: {angle}° ({mode} режим)")
                else:
                    await update.message.reply_text("❌ Не удалось установить угол")
            except ValueError:
                await update.message.reply_text("❌ Неверный формат угла")
        else:
            await update.message.reply_text(
                "🤔 Не понимаю команду. Используйте /help для справки.",
                reply_markup=self.keyboard
            )
    
    def run(self):
        """Запуск бота"""
        print("🤖 Запуск Telegram бота...")
        print(f"📊 Статус: {self.servo.get_status()}")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)