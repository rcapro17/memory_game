import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import random
import time
import os
import sqlite3


class MemoryGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Jogos Educacionais")
        self.root.geometry("800x600")
        self.revealed = []
        self.buttons = []
        self.matched_pairs = 0
        self.start_time = None
        self.timer_running = False
        self.rankings = {}
        self.theme_images = {}  # Dictionary to store the images
        self.create_initial_menu()
        self.disable_buttons()

    def create_initial_menu(self):
        self.clear_root()
        self.root.configure(bg='#2A3663')
        self.title_label = tk.Label(self.root, text="Jogos Educacionais", font=("Helvetica", 48, "bold"), fg="#2A3663", bg='white')
        self.title_label.pack(pady=50)

        self.menu_frame = tk.Frame(self.root, bg='white')
        self.menu_frame.pack(expand=True)

        themes = ["Elementos", "Estados", "Países", "Relevos"]
        theme_buttons = []

        for theme in themes:
            img_path = os.path.join('assets', 'images', f'{theme}/1.png')
            image = Image.open(img_path)
            image = image.resize((400, 250), Image.LANCZOS)  # Use LANCZOS instead of ANTIALIAS
            photo_image = ImageTk.PhotoImage(image)

            self.theme_images[theme] = photo_image  # Store the image reference

            button = tk.Button(self.menu_frame, text=theme, fg='black', width=400, height=250,
                            command=lambda t=theme: self.start_game(t), image=photo_image, compound="center")
            theme_buttons.append(button)

        for i, button in enumerate(theme_buttons):
            row = i // 2
            col = i % 2
            button.grid(row=row, column=col, padx=20, pady=20, sticky="nsew")

        # Add the rankings button using grid() instead of pack()
        show_rankings_button = tk.Button(self.menu_frame, text="Show Rankings", command=self.show_rankings)
        show_rankings_button.grid(row=len(theme_buttons) // 2, column=0, columnspan=2, pady=20)  # Position it below the theme buttons


    def clear_root(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def load_images(self, theme):
        images = []
        if theme in ["Estados", "Países", "Relevos", "Elementos"]:
            for i in range(1, 9):
                flag_img_path = os.path.join('assets', 'images', theme, f'{i}_flag.png')
                name_img_path = os.path.join('assets', 'images', theme, f'{i}_name.png')
                if not os.path.exists(flag_img_path) or not os.path.exists(name_img_path):
                    messagebox.showerror("Erro", f"Imagem não encontrada: {flag_img_path} ou {name_img_path}")
                    self.back_to_menu()
                    return []
                flag_img = Image.open(flag_img_path)
                flag_img = flag_img.resize((250, 250), Image.LANCZOS)
                images.append((ImageTk.PhotoImage(flag_img), f'{i}_flag'))

                name_img = Image.open(name_img_path)
                name_img = name_img.resize((150, 180), Image.LANCZOS)
                images.append((ImageTk.PhotoImage(name_img), f'{i}_name'))
        else:
            for i in range(1, 9):
                img_path = os.path.join('themes', theme, f'{i}.png')
                if not os.path.exists(img_path):
                    messagebox.showerror("Erro", f"Imagem não encontrada: {img_path}")
                    self.back_to_menu()
                    return []
                img = Image.open(img_path)
                img = img.resize((150, 180), Image.LANCZOS)
                images.append((ImageTk.PhotoImage(img), f'{i}'))

        random.shuffle(images)
        return images

    def back_to_menu(self):
        self.create_initial_menu()

    def update_timer(self):
        if self.timer_running:
            elapsed_time = int(time.time() - self.start_time)
            self.timer_label.config(text=f"Time: {elapsed_time}s")
            if elapsed_time <= 100:
                self.root.after(1000, self.update_timer)
            else:
                self.timer_running = False
                messagebox.showinfo("Time's up!", "You lost! Time exceeded 100 seconds.")
                self.disable_buttons()

    def create_game_board(self):
        self.clear_root()
        self.root.title(f"Jogos Educacionais - {self.theme}")
        self.root.configure(bg='white')

        self.timer_label = tk.Label(self.root, text="Time: 0s", font=("Helvetica", 14), bg='grey', fg='white')
        self.timer_label.grid(row=5, column=0, columnspan=4)

        self.create_control_buttons()

        # Create buttons for game cards
        for i in range(4):
            self.root.rowconfigure(i, weight=1)
            self.root.columnconfigure(i, weight=1)
            for j in range(4):
                idx = i * 4 + j
                button = tk.Button(self.root, text='', width=10, height=5, command=lambda idx=idx: self.reveal_image(idx),
                                   bg='gray', fg='white')
                button.grid(row=i, column=j, padx=10, pady=10, sticky="nsew")
                self.buttons.append(button)

        self.images = self.load_images(self.theme)

        # Assign shuffled images to buttons
        for idx, button in enumerate(self.buttons):
            button.image_ref = self.images[idx]

    def create_control_buttons(self):
        button_style = {'bg': '#2A3663', 'fg': 'black', 'font': ("Helvetica", 12)}
        start_button = tk.Button(self.root, text="Start", command=lambda: self.start_game(self.theme), **button_style)
        start_button.grid(row=6, column=0, columnspan=1, sticky="ew", padx=10, pady=10)

        restart_button = tk.Button(self.root, text="Restart", command=self.restart_game, **button_style)
        restart_button.grid(row=6, column=1, columnspan=1, sticky="ew", padx=10, pady=10)

        end_button = tk.Button(self.root, text="End Game", command=self.end_game, **button_style)
        end_button.grid(row=6, column=2, columnspan=1, sticky="ew", padx=10, pady=10)

        back_button = tk.Button(self.root, text="Voltar", command=self.back_to_menu, **button_style)
        back_button.grid(row=6, column=3, columnspan=1, sticky="ew", padx=10, pady=10)

    def reveal_image(self, idx):
        if not self.timer_running:
            return

        if len(self.revealed) < 2 and not hasattr(self.buttons[idx], 'revealed'):
            self.buttons[idx].config(image=self.images[idx][0])
            self.buttons[idx].revealed = True
            self.revealed.append(idx)

            if len(self.revealed) == 2:
                self.root.after(1000, self.check_match)
    def check_match(self):
        idx1, idx2 = self.revealed
        image1, tag1 = self.images[idx1]
        image2, tag2 = self.images[idx2]

        if tag1.split('_')[0] == tag2.split('_')[0] and tag1 != tag2:
            self.buttons[idx1].config(state='disabled')
            self.buttons[idx2].config(state='disabled')
            self.matched_pairs += 1
        else:
            self.buttons[idx1].config(image='', text='')
            self.buttons[idx2].config(image='', text='')
            del self.buttons[idx1].revealed
            del self.buttons[idx2].revealed

        self.revealed.clear()

        if self.matched_pairs == 8:
            elapsed_time = int(time.time() - self.start_time)
            self.timer_running = False
            messagebox.showinfo("Game Over", f"Congratulations! You finished the game in {elapsed_time} seconds.")
            self.disable_buttons()
            self.save_score(elapsed_time)
            self.show_ranking(elapsed_time)

    def save_score(self, elapsed_time):
        if not os.path.exists('database'):
            os.makedirs('database')

        conn = sqlite3.connect('database/scores.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS rankings
                     (name TEXT, theme TEXT, time INTEGER)''')
        c.execute("INSERT INTO rankings (name, theme, time) VALUES (?, ?, ?)",
                  (self.player_name, self.theme, elapsed_time))
        conn.commit()
        conn.close()
    

    def show_rankings(self):
        self.clear_root()
        self.root.title("Top 10 Rankings")
        
        # Create a button to go back to the menu
        back_button = tk.Button(self.root, text="Back to Menu", command=self.create_initial_menu, 
                                fg='black', bg='#2A3663', font=("Helvetica", 14))
        back_button.pack(pady=20)

        # Create a listbox to show the rankings
        ranking_list = tk.Listbox(self.root, font=("Helvetica", 14), width=50, height=15)
        ranking_list.pack(pady=20)

        # Fetch and display top 10 players per theme
        conn = sqlite3.connect('database/scores.db')
        c = conn.cursor()
        c.execute("SELECT name, theme, time FROM rankings ORDER BY theme, time LIMIT 10")
        rankings = c.fetchall()
        conn.close()

        for rank, (name, theme, time) in enumerate(rankings, 1):
            ranking_list.insert(tk.END, f"{rank}. {name} - {theme} - {time}s")

    def disable_buttons(self):
        for button in self.buttons:
            button.config(state='disabled')

    def start_game(self, theme):
        self.theme = theme
        self.player_name = simpledialog.askstring("Nome do Jogador", "Digite seu nome:")
        if not self.player_name:
            return

        self.images = self.load_images(theme)
        if not self.images:
            return

        self.start_time = time.time()
        self.timer_running = True
        self.matched_pairs = 0
        self.revealed = []
        self.buttons = []

        self.create_game_board()
        self.update_timer()

    def restart_game(self):
        self.start_game(self.theme)

    def end_game(self):
        self.timer_running = False
        self.back_to_menu()


if __name__ == "__main__":
    root = tk.Tk()
    app = MemoryGame(root)
    root.mainloop()