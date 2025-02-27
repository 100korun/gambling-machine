import tkinter as tk
from tkinter import ttk
import random
import pygame
import configparser
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Символы на барабанах
symbols = ['🍒', '🍋', '🍉', '🍇', '🍊', '🍍', '🍎']

# Денежные выигрыши за разные комбинации
prizes = {
    '🍒': 100, '🍋': 300, '🍉': 200, '🍇': 400,
    '🍊': 100, '🍍': 200, '🍎': 1000
}

# Добавляем малые выигрыши за пары символов (2 из 3)
pair_prizes = {
    '🍒': 10, '🍋': 30, '🍉': 20, '🍇': 20,
    '🍊': 10, '🍍': 20, '🍎': 50
}

# Файл конфигурации для сохранения настроек
CONFIG_FILE = "settings.ini"


class SettingsWindow:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app

        # Создаем новое окно
        self.window = tk.Toplevel(parent)
        self.window.title("Настройки")
        self.window.geometry("400x300")
        self.window.configure(bg="#333333")
        self.window.transient(parent)  # Привязка к родительскому окну
        self.window.grab_set()  # Делаем окно модальным

        # Стиль для виджетов
        style = ttk.Style()
        style.configure("TFrame", background="#333333")
        style.configure("TLabel", background="#333333", foreground="white", font=("Arial", 12))
        style.configure("TScale", background="#333333")

        # Основной фрейм
        main_frame = ttk.Frame(self.window, padding=20, style="TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Заголовок
        title_label = ttk.Label(main_frame, text="Настройки звука", font=("Arial", 16, "bold"), style="TLabel")
        title_label.pack(pady=(0, 20))

        # Фоновая музыка
        music_frame = ttk.Frame(main_frame, style="TFrame")
        music_frame.pack(fill=tk.X, pady=10)

        music_label = ttk.Label(music_frame, text="Громкость музыки:", style="TLabel")
        music_label.pack(side=tk.LEFT, padx=5)

        self.music_scale = ttk.Scale(music_frame, from_=0, to=1, length=200,
                                     value=self.app.music_volume, orient="horizontal")
        self.music_scale.pack(side=tk.RIGHT, padx=5)

        # Звуковые эффекты
        effects_frame = ttk.Frame(main_frame, style="TFrame")
        effects_frame.pack(fill=tk.X, pady=10)

        effects_label = ttk.Label(effects_frame, text="Громкость эффектов:", style="TLabel")
        effects_label.pack(side=tk.LEFT, padx=5)

        self.effects_scale = ttk.Scale(effects_frame, from_=0, to=1, length=200,
                                       value=self.app.effects_volume, orient="horizontal")
        self.effects_scale.pack(side=tk.RIGHT, padx=5)

        # Включение/выключение звука
        sound_frame = ttk.Frame(main_frame, style="TFrame")
        sound_frame.pack(fill=tk.X, pady=10)

        self.sound_var = tk.BooleanVar(value=self.app.sound_on)
        sound_check = ttk.Checkbutton(sound_frame, text="Включить звук", variable=self.sound_var)
        sound_check.pack(side=tk.LEFT, padx=5)

        # Кнопки внизу
        button_frame = ttk.Frame(main_frame, style="TFrame")
        button_frame.pack(fill=tk.X, pady=(20, 0))

        save_button = tk.Button(button_frame, text="Сохранить", bg="#4CAF50", fg="white",
                                font=("Arial", 12), command=self.save_settings, relief="flat")
        save_button.pack(side=tk.RIGHT, padx=5)

        cancel_button = tk.Button(button_frame, text="Отмена", bg="#f44336", fg="white",
                                  font=("Arial", 12), command=self.window.destroy, relief="flat")
        cancel_button.pack(side=tk.RIGHT, padx=5)

    def save_settings(self):
        """Сохранение настроек и их применение"""
        self.app.music_volume = self.music_scale.get()
        self.app.effects_volume = self.effects_scale.get()
        self.app.sound_on = self.sound_var.get()

        # Применяем новые настройки
        if self.app.sound_on:
            pygame.mixer.music.set_volume(self.app.music_volume)
            if not pygame.mixer.music.get_busy():
                self.app.play_music()
        else:
            pygame.mixer.music.pause()

        # Сохраняем в файл
        self.app.save_settings()
        self.window.destroy()


class GamblingMachineApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Гемблинг машина 🎰")

        self.root.geometry("840x810")

        self.root.configure(bg="#282828")

        # Блокировка повторных спинов
        self.spinning = False

        # Создаем фреймы для лучшей организации
        self.top_frame = tk.Frame(root, bg="#282828")
        self.top_frame.pack(fill=tk.X, padx=10, pady=5)

        self.game_frame = tk.Frame(root, bg="#282828")
        self.game_frame.pack(padx=10, pady=5)

        self.control_frame = tk.Frame(root, bg="#282828")
        self.control_frame.pack(fill=tk.X, padx=10, pady=5)

        self.graph_frame = tk.Frame(root, bg="#282828")
        self.graph_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Баланс
        self.start_balance = 1000
        self.balance = self.start_balance

        # Отображение баланса в верхнем фрейме
        self.balance_label = tk.Label(self.top_frame, text=f"Баланс: {self.balance} грн",
                                      font=("Arial", 16), fg="yellow", bg="#282828")
        self.balance_label.pack(side=tk.LEFT, pady=10)

        # Звуковые эффекты - инициализация
        pygame.mixer.init()
        self.config = configparser.ConfigParser()
        self.load_settings()

        # Кнопка настроек (справа)
        self.settings_button = tk.Button(self.top_frame, text="⚙️", font=("Arial", 14),
                                         command=self.open_settings, bg="#555555", fg="white",
                                         relief="flat", height=1, width=3)
        self.settings_button.pack(side=tk.RIGHT, padx=5)

        # Создаем рамку для барабанов (для лучшего визуального эффекта)
        self.reels_frame = tk.Frame(self.game_frame, bg="#333333", bd=2, relief=tk.GROOVE)
        self.reels_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        # Барабаны в специальной рамке
        self.labels = [tk.Label(self.reels_frame, text="🍒", font=("Arial", 60),
                                width=4, fg="gold", bg="#333333") for _ in range(3)]
        for i, label in enumerate(self.labels):
            label.grid(row=0, column=i, padx=15, pady=10)

        # Кнопка спина под барабанами
        self.spin_button = tk.Button(self.game_frame, text="Крутить! 🎰",
                                     font=("Arial", 18), command=self.spin,
                                     bg="#ff5722", fg="white", relief="raised",
                                     height=1, width=15)
        self.spin_button.grid(row=1, column=0, columnspan=3, pady=15)

        # Сообщение о выигрыше
        self.result_label = tk.Label(self.game_frame, text="",
                                     font=("Arial", 14), fg="yellow", bg="#282828")
        self.result_label.grid(row=2, column=0, columnspan=3, pady=10)

        # Кнопка "Играть заново" (изначально скрыта)
        self.play_again_button = tk.Button(self.game_frame, text="Играть заново 🔄",
                                           font=("Arial", 18), command=self.reset_game,
                                           bg="#4CAF50", fg="white", relief="raised",
                                           height=1, width=15)

        # График баланса
        self.spin_count = 0
        self.balance_history = [self.balance]

        self.fig, self.ax = plt.subplots(figsize=(5, 3))
        self.update_graph()

        # Запуск фоновой музыки
        if self.sound_on:
            self.play_music()

    def reset_game(self):
        """Сбросить игру и начать заново"""
        # Восстанавливаем начальный баланс
        self.balance = self.start_balance
        self.update_balance_label()

        # Обновляем историю баланса
        self.spin_count = 0
        self.balance_history = [self.balance]
        self.update_graph()

        # Удаляем кнопку "Играть заново" и показываем кнопку "Крутить"
        self.play_again_button.grid_forget()
        self.spin_button.grid(row=1, column=0, columnspan=3, pady=15)

        # Очищаем сообщение о результате
        self.result_label.config(text="Начните игру!", fg="yellow")

    def open_settings(self):
        """Открыть окно настроек"""
        settings_window = SettingsWindow(self.root, self)

    def load_settings(self):
        """Загрузка настроек из файла"""
        if os.path.exists(CONFIG_FILE):
            self.config.read(CONFIG_FILE)
            self.music_volume = float(self.config.get("Settings", "MusicVolume", fallback="0.5"))
            self.effects_volume = float(self.config.get("Settings", "EffectsVolume", fallback="0.7"))
            self.sound_on = self.config.getboolean("Settings", "SoundOn", fallback=True)
        else:
            self.music_volume = 0.5
            self.effects_volume = 0.7
            self.sound_on = True

    def save_settings(self):
        """Сохранение настроек в файл"""
        self.config["Settings"] = {
            "MusicVolume": str(self.music_volume),
            "EffectsVolume": str(self.effects_volume),
            "SoundOn": str(self.sound_on)
        }
        with open(CONFIG_FILE, "w") as configfile:
            self.config.write(configfile)

    def play_music(self):
        """Запуск фоновой музыки"""
        try:
            pygame.mixer.music.load("music.mp3")
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1)  # -1 для бесконечного повторения
        except:
            print("Ошибка загрузки музыки. Проверьте наличие файла music.mp3")

    def play_win_sound(self, mega=False):
        """Воспроизведение звука выигрыша"""
        if not self.sound_on:
            return

        try:
            # Канал 1 для звуков выигрыша (отдельно от фоновой музыки)
            if mega:
                sound = pygame.mixer.Sound("mega_win.wav")
            else:
                sound = pygame.mixer.Sound("win.wav")

            sound.set_volume(self.effects_volume)
            pygame.mixer.Channel(1).play(sound)
        except:
            print(f"Ошибка воспроизведения звука выигрыша. Проверьте наличие файлов win.wav и mega_win.wav")

    def play_spin_sound(self):
        """Воспроизведение звука при нажатии кнопки спина"""
        if not self.sound_on:
            return

        try:
            # Канал 2 для звука нажатия кнопки
            sound = pygame.mixer.Sound("spin.wav")
            sound.set_volume(self.effects_volume)
            pygame.mixer.Channel(2).play(sound)
        except:
            print("Ошибка воспроизведения звука спина. Проверьте наличие файла spin.wav")

    def spin(self):
        # Предотвращаем повторный спин пока идет анимация
        if self.spinning:
            return

        if self.balance <= 0:
            self.result_label.config(text="У вас закончились деньги!", fg="red")
            # Показываем кнопку "Играть заново"
            self.spin_button.grid_forget()
            self.play_again_button.grid(row=1, column=0, columnspan=3, pady=15)
            return

        # Воспроизводим звук нажатия кнопки
        self.play_spin_sound()

        spin_cost = 50
        self.balance -= spin_cost
        self.update_balance_label()

        # Устанавливаем флаг анимации
        self.spinning = True
        # Отключаем кнопку на время анимации
        self.spin_button.config(state=tk.DISABLED)
        # Очищаем предыдущий результат
        self.result_label.config(text="Крутим барабаны...", fg="white")

        # Запускаем анимацию поочередно для каждого барабана
        self.final_symbols = [random.choice(symbols) for _ in range(3)]
        self.start_sequential_animation(0, 20)

    def start_sequential_animation(self, reel_index, steps):
        """Запуск последовательной анимации барабанов"""
        if reel_index < len(self.labels):
            self.animate_reel(reel_index, steps, 0)
        else:
            # После остановки всех барабанов показываем результат
            self.spinning = False
            self.spin_button.config(state=tk.NORMAL)
            self.show_result()

            # Обновляем график только после завершения анимации
            self.spin_count += 1
            self.balance_history.append(self.balance)
            self.update_graph()

    def animate_reel(self, reel_index, total_steps, current_step):
        """Анимация одного барабана"""
        if current_step < total_steps:
            # Быстрое вращение в начале, замедление в конце
            delay = 30
            if current_step > total_steps * 0.7:
                delay = 30 + int(((current_step - total_steps * 0.7) / (total_steps * 0.3)) * 100)

            # Показываем случайный символ
            self.labels[reel_index].config(text=random.choice(symbols))

            # Следующий шаг анимации
            self.root.after(delay, self.animate_reel, reel_index, total_steps, current_step + 1)
        else:
            # Устанавливаем финальный символ и переходим к следующему барабану
            self.labels[reel_index].config(text=self.final_symbols[reel_index])
            # Эффект "дрожания" при остановке
            self.root.after(100, self.shake_reel, reel_index, 5)

            # Небольшая задержка перед следующим барабаном
            self.root.after(300, self.start_sequential_animation, reel_index + 1, total_steps - 5)

    def shake_reel(self, reel_index, shake_count):
        """Эффект дрожания барабана при остановке"""
        if shake_count > 0:
            # Меняем отступ для эффекта вибрации
            padding = 15 if shake_count % 2 == 0 else 16
            self.labels[reel_index].grid(row=0, column=reel_index, padx=padding, pady=10)
            self.root.after(50, self.shake_reel, reel_index, shake_count - 1)
        else:
            # Возвращаем нормальное положение
            self.labels[reel_index].grid(row=0, column=reel_index, padx=15, pady=10)

    def show_result(self):
        """Показать результат спина"""
        result = [label.cget("text") for label in self.labels]
        win_result = self.check_win(result)

        if win_result:
            if win_result[0] == "three_same":
                # Три одинаковых символа
                self.process_win(win_result[1], is_triple=True)
            elif win_result[0] == "pair":
                # Пара символов
                self.process_win(win_result[1], is_triple=False)
        else:
            self.result_label.config(text="Попробуйте снова.", fg="yellow")

    def check_win(self, result):
        """Проверка выигрышной комбинации
        Возвращает:
        - ("three_same", символ) если все три символа одинаковые
        - ("pair", символ) если два символа одинаковые
        - None если нет выигрышной комбинации
        """
        # Проверка на три одинаковых
        if len(set(result)) == 1:
            return ("three_same", result[0])

        # Проверка на пару
        for symbol in symbols:
            if result.count(symbol) == 2:
                return ("pair", symbol)

        return None

    def process_win(self, symbol, is_triple=True):
        """Обработка выигрыша"""
        if is_triple:
            win_amount = prizes.get(symbol, 0)
            win_text = f"КОМБО: три {symbol}! Вы выиграли {win_amount} грн! 🎉"
        else:
            win_amount = pair_prizes.get(symbol, 0)
            win_text = f"ПАРА {symbol}! Вы выиграли {win_amount} грн!"

        self.balance += win_amount
        self.update_balance_label()

        # Определяем, мега-выигрыш это или обычный
        is_mega_win = win_amount >= 200

        if is_mega_win:
            self.result_label.config(text=f"МЕГА ВЫИГРЫШ: {win_amount} грн! 🎉", fg="#00ffff")
            self.play_win_sound(mega=True)
        else:
            self.result_label.config(text=win_text, fg="yellow")
            self.play_win_sound(mega=False)

    def update_balance_label(self):
        """Обновление отображения баланса"""
        self.balance_label.config(text=f"Баланс: {self.balance} грн")

    def update_graph(self):
        """Обновление графика баланса"""
        self.ax.clear()
        self.ax.set_facecolor("#333333")
        self.fig.patch.set_facecolor("#282828")

        for spine in self.ax.spines.values():
            spine.set_color("#282828")

        self.ax.set_title('График баланса', fontsize=14, color='yellow')
        self.ax.set_xlabel('Спины', fontsize=10, color='yellow')
        self.ax.set_ylabel('Баланс', fontsize=10, color='yellow')

        self.ax.tick_params(axis='x', colors='yellow')
        self.ax.tick_params(axis='y', colors='yellow')

        self.ax.plot(self.balance_history, color="red", label="Баланс", linewidth=2)
        self.ax.legend(facecolor='#282828', edgecolor='yellow', fontsize=8)

        if not hasattr(self, 'canvas'):
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = GamblingMachineApp(root)
    root.mainloop()