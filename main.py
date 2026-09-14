# ==========================================
# Archivo: main.py
# ==========================================
import tkinter as tk
from gui import InterfazCompilador

if __name__ == '__main__':
    raiz = tk.Tk()
    app = InterfazCompilador(raiz)
    raiz.mainloop()
    