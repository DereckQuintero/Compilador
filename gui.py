# ==========================================
# Archivo: gui.py
# ==========================================
import tkinter as tk
from tkinter import scrolledtext
from scanner import Scanner, ErrorLexico
from parser_sintactico import Parser

class InterfazCompilador:
    def __init__(self, ventana_raiz):
        self.ventana = ventana_raiz
        self.ventana.title("Compilador - Fases de Análisis")
        self.ventana.geometry("750x600")
        self.ventana.config(padx=15, pady=15)
        
        self.scanner = Scanner()
        self._construir_interfaz()

    def _construir_interfaz(self):
        tk.Label(self.ventana, text="1. Ingresa el código fuente (Programa):", font=("Arial", 10, "bold")).pack(anchor='w')
        self.entrada_texto = scrolledtext.ScrolledText(self.ventana, width=80, height=8, font=("Consolas", 10))
        self.entrada_texto.pack(pady=5)
        
        # Código de prueba del documento base
        codigo_prueba = "x = a @ b == 5;\nif (x > 100) {\n    y = 42 # 1;\n}"
        self.entrada_texto.insert(tk.END, codigo_prueba)

        self.boton_analizar = tk.Button(self.ventana, text="Analizar Código", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), command=self.ejecutar_analisis)
        self.boton_analizar.pack(pady=10)

        panel_inferior = tk.Frame(self.ventana)
        panel_inferior.pack(fill="both", expand=True)

        frame_tokens = tk.Frame(panel_inferior)
        frame_tokens.pack(side="left", fill="both", expand=True, padx=(0, 10))
        tk.Label(frame_tokens, text="2. Tokens Generados:", font=("Arial", 10, "bold")).pack(anchor="w")
        self.salida_tokens = scrolledtext.ScrolledText(frame_tokens, width=40, height=14, font=("Consolas", 10))
        self.salida_tokens.pack(fill="both", expand=True)

        frame_parser = tk.Frame(panel_inferior)
        frame_parser.pack(side="right", fill="both", expand=True, padx=(10, 0))
        tk.Label(frame_parser, text="3. Resultado del Parser:", font=("Arial", 10, "bold")).pack(anchor="w")
        self.salida_parser = tk.Text(frame_parser, width=40, height=14, font=("Consolas", 11, "bold"))
        self.salida_parser.pack(fill="both", expand=True)

    def ejecutar_analisis(self):
        codigo = self.entrada_texto.get("1.0", tk.END).strip()
        if not codigo: return

        self.salida_tokens.delete("1.0", tk.END)
        self.salida_parser.delete("1.0", tk.END)
        
        try:
            # 1. Scanner
            tokens = self.scanner.analizar(codigo)
            self.salida_tokens.insert(tk.END, "LEXEMA\t\tTIPO\t\tCÓDIGO\n")
            self.salida_tokens.insert(tk.END, "-"*45 + "\n")
            for t in tokens:
                if t['tipo'] != 'EOF':
                    self.salida_tokens.insert(tk.END, f"{t['lexema']:<12}\t{t['tipo']:<15}\t{t['codigo']}\n")

            # 2. Parser
            parser = Parser(tokens)
            exito, mensaje = parser.analizar()
            
            self.salida_parser.config(fg="green" if exito else "red")
            self.salida_parser.insert(tk.END, "\n" + mensaje)
            
        except ErrorLexico as error:
            self.salida_tokens.insert(tk.END, f"\n¡ERROR!\n{error}")
            self.salida_parser.config(fg="red")
            self.salida_parser.insert(tk.END, "\nEl análisis sintáctico no inició debido a un error léxico.")