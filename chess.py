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
        # guard: click inside board
        if not (0 <= r < 8 and 0 <= c < 8):
            return
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
            return
        self.turn = "black" if self.turn == "white" else "white"
        self.status.config(text=f"{self.turn.capitalize()}'s Turn")

    # -------------------------
    # Helpers for check logic
    # -------------------------
    def find_king(self, board, color):
        """Return (r,c) of king for color ('white' or 'black') on given board or None."""
        king_symbol = "K" if color == "white" else "k"
        for r in range(8):
            for c in range(8):
                if board[r][c] == king_symbol:
                    return (r, c)
        return None

    def is_valid_move(self, sr, sc, tr, tc, board=None):
        """
        Validate move from (sr,sc) to (tr,tc) on provided board (defaults to self.board).
        Note: This only checks piece movement rules and blocking; it DOES NOT check whether the move
        would leave own king in check. Use move_causes_check to filter such moves.
        """
        if board is None:
            board = self.board

        piece = board[sr][sc]
        target = board[tr][tc]
        if piece == ".":
            return False
        if (sr, sc) == (tr, tc):
            return False
        # same-color capture not allowed
        if target != "." and ((piece.isupper() and target.isupper()) or (piece.islower() and target.islower())):
            return False
        dr, dc = tr - sr, tc - sc
        absr, absc = abs(dr), abs(dc)

        # Pawn
        if piece == "P":
            if dc == 0 and board[tr][tc] == ".":
                if dr == -1: return True
                if dr == -2 and sr == 6 and board[sr-1][sc] == ".": return True
            if abs(dc) == 1 and dr == -1 and target != "." and target.islower(): return True
            return False
        if piece == "p":
            if dc == 0 and board[tr][tc] == ".":
                if dr == 1: return True
                if dr == 2 and sr == 1 and board[sr+1][sc] == ".": return True
            if abs(dc) == 1 and dr == 1 and target != "." and target.isupper(): return True
            return False

        # Rook
        if piece.lower() == "r":
            if dr == 0 or dc == 0:
                if self.clear_path(sr, sc, tr, tc, board): return True
            return False

        # Bishop
        if piece.lower() == "b":
            if absr == absc and self.clear_path(sr, sc, tr, tc, board): return True
            return False

        # Queen
        if piece.lower() == "q":
            if (dr == 0 or dc == 0 or absr == absc) and self.clear_path(sr, sc, tr, tc, board): return True
            return False

        # Knight
        if piece.lower() == "n":
            if (absr, absc) in [(1, 2), (2, 1)]: return True
            return False

        # King
        if piece.lower() == "k":
            if absr <= 1 and absc <= 1: return True
            return False

        return False

    def clear_path(self, sr, sc, tr, tc, board=None):
        """Check that squares between source and target are empty on given board."""
        if board is None:
            board = self.board
        dr, dc = tr - sr, tc - sc
        step_r = (dr // abs(dr)) if dr != 0 else 0
        step_c = (dc // abs(dc)) if dc != 0 else 0
        r, c = sr + step_r, sc + step_c
        while (r, c) != (tr, tc):
            if board[r][c] != ".":
                return False
            r += step_r
            c += step_c
        return True

    def is_square_attacked(self, board, r, c, by_color):
        """
        Returns True if square (r,c) on given board is attacked by any piece of by_color.
        by_color: 'white' or 'black'
        """
        for sr in range(8):
            for sc in range(8):
                piece = board[sr][sc]
                if piece == ".":
                    continue
                if by_color == "white" and not piece.isupper():
                    continue
                if by_color == "black" and not piece.islower():
                    continue
                # use is_valid_move on the given board to test if that piece can move to (r,c)
                if self.is_valid_move(sr, sc, r, c, board):
                    return True
        return False

    def move_causes_check(self, sr, sc, tr, tc):
        """
        Simulate move from (sr,sc) to (tr,tc) and return True if after move,
        the moving side's king is in check.
        """
        # make a deep copy of board (simple row copies are sufficient)
        temp = [row[:] for row in self.board]
        piece = temp[sr][sc]
        temp[tr][tc] = piece
        temp[sr][sc] = "."

        color = "white" if piece.isupper() else "black"
        king_pos = self.find_king(temp, color)
        if king_pos is None:
            # should not happen normally, but assume not in check
            return False
        kr, kc = king_pos
        opponent = "black" if color == "white" else "white"
        return self.is_square_attacked(temp, kr, kc, opponent)

    # -------------------------
    # Move generation (filtered by check)
    # -------------------------
    def get_valid_moves(self, sr, sc):
        piece = self.board[sr][sc]
        moves = []
        if piece == ".":
            return moves
        for tr in range(8):
            for tc in range(8):
                # first check basic movement rules on current board
                if self.is_valid_move(sr, sc, tr, tc, self.board):
                    # then ensure the move doesn't leave/make own king in check
                    if not self.move_causes_check(sr, sc, tr, tc):
                        moves.append((tr, tc))
        return moves

if __name__ == "__main__":
    root = tk.Tk()
    game = ChessGame(root)
    root.mainloop()
