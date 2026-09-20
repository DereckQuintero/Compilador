# ==========================================
# Archivo: main.py
# ==========================================
if __name__ == '__main__':
    try:
        import tkinter as tk
        from gui import InterfazCompilador
        raiz = tk.Tk()
        app = InterfazCompilador(raiz)
        raiz.mainloop()
    except ModuleNotFoundError as error:
        if error.name == 'tkinter':
            print('Falta Tkinter. Instálalo con: sudo apt install python3-tk')
        else:
            raise
    