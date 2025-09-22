import tkinter as tk

class RoundedButton:
    def __init__(self, x, y, width, height, background, foreground, text, command, radius: int = 6, tkparent = None):
        self._tkparent = tkparent
        w  = int(str(width))
        h  = int(str(height))
        r  = int(str(radius))
        bg = background
        fg = foreground
        self._arc1 = self._tkparent.create_arc((x, y, x + 2 * r, y + 2 * r), start=90, extent=90, fill=bg, outline=bg)
        self._arc2 = self._tkparent.create_arc((x + w - 2 * r, y, x + w, y + 2 * r), start=0, extent=90, fill=bg, outline=bg)
        self._arc3 = self._tkparent.create_arc((x, y + h - 2 * r, x + 2 * r, y + h), start=180, extent=90, fill=bg, outline=bg)
        self._arc4 = self._tkparent.create_arc((x + w - 2 * r, y + h - 2 * r, x + w, y + h), start=270, extent=90, fill=bg, outline=bg)
        self._rct1 = self._tkparent.create_rectangle(x + r, y, x + w - r, y + h, fill = bg, outline = bg)
        self._rct2 = self._tkparent.create_rectangle(x, y + r, x + w, y + h - r, fill=bg, outline=bg)
        self._cnvs = tk.Canvas(self._tkparent, width= w - 2 - r // 2, height=h - 2 - r // 2, bg=bg, highlightthickness=0)
        self._tkparent.create_window(x + 1 + w//2, y + 1 + h//2, window=self._cnvs)
        self._cnvs.create_text(0 + (w - 2 - r)//2, 0 + (h - 2 - r)//2, text=text, fill=fg, font=("Arial", 15))
        self._cnvs.bind("<Button-1>", lambda e: command())
        self._cnvs.bind("<Enter>", lambda e: self._cnvs.config(cursor="hand2"))
        self._cnvs.bind("<Leave>", lambda e: self._cnvs.config(cursor=""))
    
    def destroy(self):
        self._tkparent.delete(self._arc1)
        self._tkparent.delete(self._arc2)
        self._tkparent.delete(self._arc3)
        self._tkparent.delete(self._arc4)
        self._tkparent.delete(self._rct1)
        self._tkparent.delete(self._rct2)
        self._cnvs.destroy()
