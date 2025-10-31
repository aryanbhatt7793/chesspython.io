import tkinter as tk
from tkinter import messagebox

PIECES = {
    "r": "♜", "n": "♞", "b": "♝", "q": "♛", "k": "♚", "p": "♟",
    "R": "♖", "N": "♘", "B": "♗", "Q": "♕", "K": "♔", "P": "♙"
}

START = [
    list("rnbqkbnr"),
    list("pppppppp"),
    list("........"),
    list("........"),
    list("........"),
    list("........"),
    list("PPPPPPPP"),
    list("RNBQKBNR")
]

class ChessGame:
    def __init__(self, root):
        self.root = root
        self.root.title("♞ Beautiful Smart Chess")
        self.cell = 80
        self.canvas = tk.Canvas(root, width=8*self.cell, height=8*self.cell)
        self.canvas.pack()
        self.status = tk.Label(root, text="White's Turn", font=("Arial", 14))
        self.status.pack()
        self.turn = "white"
        self.board = [r[:] for r in START]
        self.selected = None
        self.valid_moves = []
        self.canvas.bind("<Button-1>", self.click)
        self.draw_board()

    def draw_board(self):
        self.canvas.delete("all")
        colors = ["#f0d9b5", "#b58863"]
        for r in range(8):
            for c in range(8):
                x1, y1 = c*self.cell, r*self.cell
                color = colors[(r+c) % 2]
                self.canvas.create_rectangle(x1, y1, x1+self.cell, y1+self.cell, fill=color, outline="")
                piece = self.board[r][c]
                if piece != ".":
                    self.canvas.create_text(x1+self.cell/2, y1+self.cell/2, text=PIECES[piece], font=("Arial", 44))
        # Highlight selected piece
        if self.selected:
            r, c = self.selected
            x1, y1 = c*self.cell, r*self.cell
            self.canvas.create_rectangle(x1, y1, x1+self.cell, y1+self.cell, outline="red", width=3)
        # Show dots for valid moves
        for (r, c) in self.valid_moves:
            x, y = c*self.cell + self.cell/2, r*self.cell + self.cell/2
            self.canvas.create_oval(x-10, y-10, x+10, y+10, fill="gray30", outline="")

    def click(self, e):
        c, r = e.x // self.cell, e.y // self.cell
        if self.selected:
            sr, sc = self.selected
            if (r, c) in self.valid_moves:
                self.make_move(sr, sc, r, c)
            self.selected = None
            self.valid_moves = []
        else:
            piece = self.board[r][c]
            if piece != "." and ((self.turn == "white" and piece.isupper()) or (self.turn == "black" and piece.islower())):
                self.selected = (r, c)
                self.valid_moves = self.get_valid_moves(r, c)
        self.draw_board()

    def make_move(self, sr, sc, tr, tc):
        piece = self.board[sr][sc]
        target = self.board[tr][tc]
        self.board[tr][tc] = piece
        self.board[sr][sc] = "."
        # Pawn promotion
        if piece == "P" and tr == 0:
            self.board[tr][tc] = "Q"
        if piece == "p" and tr == 7:
            self.board[tr][tc] = "q"
        # Win
        if target.lower() == "k":
            winner = "White" if piece.isupper() else "Black"
            messagebox.showinfo("Game Over", f"{winner} wins!")
            self.root.destroy()
        self.turn = "black" if self.turn == "white" else "white"
        self.status.config(text=f"{self.turn.capitalize()}'s Turn")

    def get_valid_moves(self, sr, sc):
        piece = self.board[sr][sc]
        moves = []
        for tr in range(8):
            for tc in range(8):
                if self.is_valid_move(sr, sc, tr, tc):
                    moves.append((tr, tc))
        return moves

    def is_valid_move(self, sr, sc, tr, tc):
        piece = self.board[sr][sc]
        target = self.board[tr][tc]
        if (sr, sc) == (tr, tc): return False
        if target != "." and ((piece.isupper() and target.isupper()) or (piece.islower() and target.islower())):
            return False
        dr, dc = tr - sr, tc - sc
        absr, absc = abs(dr), abs(dc)

        # Pawn
        if piece == "P":
            if dc == 0 and self.board[tr][tc] == ".":
                if dr == -1: return True
                if dr == -2 and sr == 6 and self.board[sr-1][sc] == ".": return True
            if abs(dc) == 1 and dr == -1 and target.islower(): return True
        if piece == "p":
            if dc == 0 and self.board[tr][tc] == ".":
                if dr == 1: return True
                if dr == 2 and sr == 1 and self.board[sr+1][sc] == ".": return True
            if abs(dc) == 1 and dr == 1 and target.isupper(): return True

        # Rook
        if piece.lower() == "r":
            if dr == 0 or dc == 0:
                if self.clear_path(sr, sc, tr, tc): return True

        # Bishop
        if piece.lower() == "b":
            if absr == absc and self.clear_path(sr, sc, tr, tc): return True

        # Queen
        if piece.lower() == "q":
            if (dr == 0 or dc == 0 or absr == absc) and self.clear_path(sr, sc, tr, tc): return True

        # Knight
        if piece.lower() == "n":
            if (absr, absc) in [(1, 2), (2, 1)]: return True

        # King
        if piece.lower() == "k":
            if absr <= 1 and absc <= 1: return True

        return False

    def clear_path(self, sr, sc, tr, tc):
        dr, dc = tr - sr, tc - sc
        step_r = (dr // abs(dr)) if dr != 0 else 0
        step_c = (dc // abs(dc)) if dc != 0 else 0
        r, c = sr + step_r, sc + step_c
        while (r, c) != (tr, tc):
            if self.board[r][c] != ".":
                return False
            r += step_r
            c += step_c
        return True


if __name__ == "__main__":
    root = tk.Tk()
    game = ChessGame(root)
    root.mainloop()
