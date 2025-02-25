import tkinter as tk
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
    '🍒': 10, '🍋': 20, '🍉': 30, '🍇': 50,
    '🍊': 100, '🍍': 200, '🍎': 1000
}

# Файл конфигурации для сохранения настроек
CONFIG_FILE = "settings.ini"

class GamblingMachineApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Гемблинг машина 🎰")
        self.root.geometry("840x810")
        self.root.configure(bg="#282828")

        # Баланс
        self.start_balance = 1000
        self.balance = self.start_balance

        # Отображение баланса
        self.balance_label = tk.Label(root, text=f"Баланс: {self.balance} грн", font=("Arial", 16), fg="yellow", bg="#282828")
        self.balance_label.grid(row=0, column=0, columnspan=3, pady=10)

        # Барабаны
        self.labels = [tk.Label(root, text="🍒", font=("Arial", 60), width=5, fg="gold", bg="#282828") for _ in range(3)]
        for i, label in enumerate(self.labels):
            label.grid(row=1, column=i, padx=15)

        # Кнопка спина
        self.spin_button = tk.Button(root, text="Нажми для спина", font=("Arial", 18), command=self.spin,
                                     bg="#ff5722", fg="white", relief="flat", height=2, width=20)
        self.spin_button.grid(row=2, column=0, columnspan=3, pady=20)

        # Сообщение о выигрыше
        self.result_label = tk.Label(root, text="", font=("Arial", 14), fg="yellow", bg="#282828")
        self.result_label.grid(row=3, column=0, columnspan=3, pady=10)

        # Музыка
        pygame.mixer.init()
        self.config = configparser.ConfigParser()
        self.load_settings()

        # Громкость
        self.volume_slider = tk.Scale(root, from_=0, to=1, resolution=0.1, orient="horizontal",
                                      command=self.set_volume, bg="#282828", fg="yellow", font=("Arial", 12))
        self.volume_slider.set(self.volume)
        self.volume_slider.grid(row=5, column=1, pady=10, columnspan=2)

        # Кнопки звука
        self.sound_button = tk.Button(root, text="🔊" if self.sound_on else "🔇", font=("Arial", 18),
                                      command=self.toggle_sound, bg="#4CAF50" if self.sound_on else "red", fg="white", relief="flat", height=1, width=5)
        self.sound_button.grid(row=5, column=0, pady=10)

        # График баланса
        self.spin_count = 0
        self.balance_history = [self.balance]

        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        self.update_graph()

        # Запуск музыки
        if self.sound_on:
            self.play_music()

    def load_settings(self):
        """Загрузка настроек из файла"""
        if os.path.exists(CONFIG_FILE):
            self.config.read(CONFIG_FILE)
            self.volume = float(self.config.get("Settings", "Volume", fallback="0.5"))
            self.sound_on = self.config.getboolean("Settings", "SoundOn", fallback=True)
        else:
            self.volume = 0.5
            self.sound_on = True

    def save_settings(self):
        """Сохранение настроек в файл"""
        self.config["Settings"] = {"Volume": str(self.volume), "SoundOn": str(self.sound_on)}
        with open(CONFIG_FILE, "w") as configfile:
            self.config.write(configfile)

    def play_music(self):
        """Запуск музыки"""
        pygame.mixer.music.load("music.mp3")
        pygame.mixer.music.set_volume(self.volume)
        pygame.mixer.music.play(-1)

    def stop_music(self):
        """Полное выключение музыки"""
        pygame.mixer.music.stop()
        self.sound_on = False
        self.sound_button.config(text="🔇", bg="red")
        self.save_settings()

    def set_volume(self, volume):
        """Установка громкости"""
        self.volume = float(volume)
        pygame.mixer.music.set_volume(self.volume)
        self.save_settings()

    def toggle_sound(self):
        """Включение/выключение звука"""
        if self.sound_on:
            pygame.mixer.music.pause()
            self.sound_button.config(text="🔇", bg="red")
        else:
            pygame.mixer.music.unpause()
            self.sound_button.config(text="🔊", bg="#4CAF50")
        self.sound_on = not self.sound_on
        self.save_settings()

    def spin(self):
        if self.balance <= 0:
            self.result_label.config(text="У вас закончились деньги!", fg="red")
            return

        spin_cost = 50
        self.balance -= spin_cost
        self.update_balance_label()

        self.animate_spin_step(0)
        self.spin_count += 1
        self.balance_history.append(self.balance)

        self.update_graph()

    def animate_spin_step(self, step):
        if step < 20:
            self.animate_spin()
            self.root.after(50, self.animate_spin_step, step + 1)
        else:
            self.show_result()

    def animate_spin(self):
        for label in self.labels:
            label.config(text=random.choice(symbols))

    def show_result(self):
        result = [label.cget("text") for label in self.labels]
        win_symbol = self.check_win(result)
        if win_symbol:
            self.process_win(win_symbol)
        else:
            self.result_label.config(text="Попробуйте снова.", fg="yellow")

    def check_win(self, result):
        return result[0] if len(set(result)) == 1 else None

    def process_win(self, symbol):
        win_amount = prizes.get(symbol, 0)
        self.balance += win_amount
        self.update_balance_label()
        self.result_label.config(text=f"Вы выиграли {win_amount} грн!", fg="yellow")

        self.balance_history.append(self.balance)
        self.update_graph()

    def update_balance_label(self):
        self.balance_label.config(text=f"Баланс: {self.balance} грн")

    def update_graph(self):
        self.ax.clear()
        self.ax.set_facecolor("#333333")
        self.fig.patch.set_facecolor("#282828")

        for spine in self.ax.spines.values():
            spine.set_color("#282828")

        self.ax.set_title('График баланса', fontsize=16, color='yellow')
        self.ax.set_xlabel('Количество спинов', fontsize=12, color='yellow')
        self.ax.set_ylabel('Баланс', fontsize=12, color='yellow')

        self.ax.tick_params(axis='x', colors='yellow')
        self.ax.tick_params(axis='y', colors='yellow')

        self.ax.plot(self.balance_history, color="red", label="Баланс", linewidth=2)
        self.ax.legend(facecolor='#282828', edgecolor='yellow', fontsize=10)

        if not hasattr(self, 'canvas'):
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
            self.canvas.get_tk_widget().grid(row=4, column=0, columnspan=3, pady=20)

        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = GamblingMachineApp(root)
    root.mainloop()
