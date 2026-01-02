import tkinter as tk
from tkinter import messagebox
import random
import time

# Constants
BOARD_SIZE = 10
CELL_SIZE = 60
WINDOW_SIZE = BOARD_SIZE * CELL_SIZE
PLAYER_COLORS = ["red", "blue", "green", "yellow"]
NUM_PLAYERS = 4

class SnakeAndLadderGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Snake and Ladder")
        self.geometry(f"{WINDOW_SIZE + 200}x{WINDOW_SIZE + 50}")
        self.resizable(False, False)

        self.canvas = tk.Canvas(self, width=WINDOW_SIZE, height=WINDOW_SIZE, bg="white")
        self.canvas.grid(row=0, column=0, rowspan=10)

        self.control_frame = tk.Frame(self)
        self.control_frame.grid(row=0, column=1, padx=20)
        
        self.dice_label = tk.Label(self.control_frame, text="Dice: -", font=("Helvetica", 16))
        self.dice_label.pack(pady=10)

        self.roll_button = tk.Button(self.control_frame, text="Roll Dice", command=self.roll_dice, font=("Helvetica", 14))
        self.roll_button.pack(pady=10)

        self.player_turn_label = tk.Label(self.control_frame, text="Player 1's Turn", font=("Helvetica", 14), fg=PLAYER_COLORS[0])
        self.player_turn_label.pack(pady=10)
        
        self.player_positions_label = tk.Label(self.control_frame, text="", font=("Helvetica", 12), justify=tk.LEFT)
        self.player_positions_label.pack(pady=20)


        self.snakes_and_ladders = {
            # Snakes
            17: 7, 54: 34, 62: 19, 64: 60, 87: 24, 93: 73, 95: 75, 99: 78,
            # Ladders
            4: 14, 9: 31, 20: 38, 28: 84, 40: 59, 51: 67, 63: 81, 71: 91
        }
        
        self.draw_board()
        self.draw_snakes_and_ladders()
        self.initialize_game()
        self.update_player_positions_display()

    def initialize_game(self):
        self.player_positions = [0] * NUM_PLAYERS
        self.player_icons = []
        for i in range(NUM_PLAYERS):
            x, y = self.get_coords(1)
            # Offset for multiple players at the same spot
            offset_x = (i % 2) * 20 - 10
            offset_y = (i // 2) * 20 - 10
            icon = self.canvas.create_oval(x - 15 + offset_x, y - 15 + offset_y, x + 15 + offset_x, y + 15 + offset_y, fill=PLAYER_COLORS[i], outline="black")
            self.player_icons.append(icon)

        self.current_player = 0
        self.game_over = False
        self.roll_button.config(state=tk.NORMAL)

    def draw_board(self):
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                x1 = j * CELL_SIZE
                y1 = i * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                
                # Determine cell number
                row = BOARD_SIZE - 1 - i
                if row % 2 == 0:
                    num = row * BOARD_SIZE + j + 1
                else:
                    num = row * BOARD_SIZE + (BOARD_SIZE - 1 - j) + 1
                
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black")
                self.canvas.create_text(x1 + CELL_SIZE/2, y1 + CELL_SIZE/2, text=str(num), font=("Helvetica", 12))
    
    def draw_snakes_and_ladders(self):
        for start, end in self.snakes_and_ladders.items():
            x1, y1 = self.get_coords(start)
            x2, y2 = self.get_coords(end)
            color = "red" if start > end else "green"
            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=3, arrow=tk.LAST)

    def get_coords(self, cell_num):
        if cell_num == 0:
            # Position players off-board initially, but get_coords for 1 to draw them near start
             return self.get_coords(1)
        
        cell_num -= 1
        row = cell_num // BOARD_SIZE
        col = cell_num % BOARD_SIZE

        if row % 2 != 0:
            col = BOARD_SIZE - 1 - col

        y = WINDOW_SIZE - (row * CELL_SIZE) - CELL_SIZE / 2
        x = col * CELL_SIZE + CELL_SIZE / 2
        return x, y

    def roll_dice(self):
        if self.game_over:
            return
            
        self.roll_button.config(state=tk.DISABLED)
        dice_roll = random.randint(1, 6)
        self.dice_label.config(text=f"Dice: {dice_roll}")
        self.move_player(dice_roll)

    def move_player(self, dice_roll):
        current_pos = self.player_positions[self.current_player]
        
        # Player needs a 1 to get on the board
        if current_pos == 0:
            if dice_roll == 1:
                new_pos = 1
            else:
                self.next_turn()
                return
        else:
             new_pos = current_pos + dice_roll

        if new_pos > 100:
            self.next_turn()
            return
            
        self.animate_move(self.current_player, current_pos, new_pos)

    def animate_move(self, player_index, start_pos, end_pos):
        # If player is at start, begin animation from cell 1
        start_anim_pos = 1 if start_pos == 0 else start_pos

        for i in range(start_anim_pos, end_pos + 1):
            x, y = self.get_coords(i)
            
            # Apply offset for icon
            offset_x = (player_index % 2) * 20 - 10
            offset_y = (player_index // 2) * 20 - 10

            self.canvas.coords(self.player_icons[player_index], x - 15 + offset_x, y - 15 + offset_y, x + 15 + offset_x, y + 15 + offset_y)
            self.update()
            time.sleep(0.1)
        
        self.player_positions[player_index] = end_pos
        self.handle_snake_or_ladder(player_index, end_pos)

    def handle_snake_or_ladder(self, player_index, pos):
        if pos in self.snakes_and_ladders:
            final_pos = self.snakes_and_ladders[pos]
            message = "Oops! Bitten by a snake!" if pos > final_pos else "Wow! Climbed a ladder!"
            messagebox.showinfo("Snake or Ladder", message)
            
            # Animate the move along the snake or ladder
            start_x, start_y = self.get_coords(pos)
            end_x, end_y = self.get_coords(final_pos)
            
            # Apply offset
            offset_x = (player_index % 2) * 20 - 10
            offset_y = (player_index // 2) * 20 - 10
            start_x += offset_x
            start_y += offset_y
            end_x += offset_x
            end_y += offset_y

            steps = 20
            for i in range(steps + 1):
                x = start_x + (end_x - start_x) * i / steps
                y = start_y + (end_y - start_y) * i / steps
                self.canvas.coords(self.player_icons[player_index], x - 15, y - 15, x + 15, y + 15)
                self.update()
                time.sleep(0.02)
            
            self.player_positions[player_index] = final_pos
            
        self.check_for_win()

    def check_for_win(self):
        if self.player_positions[self.current_player] == 100:
            self.game_over = True
            winner = self.current_player + 1
            messagebox.showinfo("Game Over", f"Player {winner} wins!")
            self.roll_button.config(state=tk.DISABLED)
        else:
            self.next_turn()
            
    def next_turn(self):
        self.update_player_positions_display()
        self.current_player = (self.current_player + 1) % NUM_PLAYERS
        self.player_turn_label.config(text=f"Player {self.current_player + 1}'s Turn", fg=PLAYER_COLORS[self.current_player])
        if not self.game_over:
            self.roll_button.config(state=tk.NORMAL)
    
    def update_player_positions_display(self):
        pos_text = "Player Positions:\n"
        for i in range(NUM_PLAYERS):
            pos = self.player_positions[i]
            pos_text += f"Player {i+1}: {pos if pos != 0 else 'Start'}\n"
        self.player_positions_label.config(text=pos_text)


if __name__ == "__main__":
    game = SnakeAndLadderGame()
    game.mainloop()
