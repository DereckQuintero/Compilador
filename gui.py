# ==========================================
# Archivo: gui.py
# ==========================================
import tkinter as tk
from tkinter import scrolledtext
from scanner import Scanner
from parser_sintactico import Parser
from analizador_semantico import AnalizadorSemantico
from generador_codigo import GeneradorCodigoIntermedio

class InterfazCompilador:
    def __init__(self, ventana_raiz):
        self.ventana = ventana_raiz
        self.ventana.title("LispScript - Fases Completas (Inc. Cód. Intermedio)")
        self.ventana.geometry("1200x750") 
        
        self.scanner = Scanner()
        self._construir_interfaz()

    def _construir_interfaz(self):
        # Panel superior de entrada
        self.entrada_texto = scrolledtext.ScrolledText(self.ventana, width=130, height=7)
        self.entrada_texto.pack(pady=10)
        
        # Código de prueba basado exactamente en tu pizarrón
        codigo_prueba = "int A, B;\nfloat diam;\nchar resp;\nstring nom;\nint valor;\nA = B @ diam;"
        self.entrada_texto.insert(tk.END, codigo_prueba)

        # Creación del botón
        tk.Button(self.ventana, text="Compilar LispScript", bg="#4CAF50", fg="white", 
                  font=("Arial", 10, "bold"), command=self.ejecutar_analisis).pack(pady=5)

        # Contenedor Grid 2x2 para los 4 paneles
        panel_inferior = tk.Frame(self.ventana)
        panel_inferior.pack(fill="both", expand=True, padx=10, pady=10)

        # 1. Scanner (Arriba Izquierda)
        self.salida_scanner = scrolledtext.ScrolledText(panel_inferior, width=40, height=15)
        self.salida_scanner.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        # 2. Parser (Arriba Derecha)
        self.salida_parser = scrolledtext.ScrolledText(panel_inferior, width=40, height=15)
        self.salida_parser.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        # 3. Semántico (Abajo Izquierda)
        self.salida_semantico = scrolledtext.ScrolledText(panel_inferior, width=40, height=15)
        self.salida_semantico.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        # 4. Código Intermedio (Abajo Derecha)
        self.salida_codigo = scrolledtext.ScrolledText(panel_inferior, width=40, height=15)
        self.salida_codigo.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        
        # Configurar expansión del grid
        panel_inferior.grid_columnconfigure(0, weight=1)
        panel_inferior.grid_columnconfigure(1, weight=1)
        panel_inferior.grid_rowconfigure(0, weight=1)
        panel_inferior.grid_rowconfigure(1, weight=1)

    def ejecutar_analisis(self):
        codigo = self.entrada_texto.get("1.0", tk.END).strip()
        
        self.salida_scanner.delete("1.0", tk.END)
        self.salida_parser.delete("1.0", tk.END)
        self.salida_semantico.delete("1.0", tk.END)
        self.salida_codigo.delete("1.0", tk.END)
        
        try:
            # 1. Scanner
            tokens = self.scanner.analizar(codigo)
            self.salida_scanner.insert(tk.END, "--- LÉXICO ---\n")
            for t in tokens: 
                self.salida_scanner.insert(tk.END, f"{t['lexema']} -> {t['tipo']}\n")

            # 2. Parser
            parser = Parser(tokens)
            arbol_ast = parser.analizar()
            self.salida_parser.insert(tk.END, "--- SINTÁCTICO (AST) ---\n")
            for nodo in arbol_ast: 
                self.salida_parser.insert(tk.END, f"{nodo}\n\n")

            # 3. Semántico
            semantico = AnalizadorSemantico()
            errores, tabla = semantico.analizar(arbol_ast)
            
            self.salida_semantico.insert(tk.END, "--- SEMÁNTICO (TS) ---\n")
            self.salida_semantico.insert(tk.END, "Nombre\tTipo\tMemoria\n" + "-"*30 + "\n")
            for nombre, info in tabla.items():
                self.salida_semantico.insert(tk.END, f"{nombre}\t{info['tipo']}\t{info['direccion']}\n")

            # 4. Generación de Código Intermedio (Solo Directivas)
            if not errores:
                generador = GeneradorCodigoIntermedio(tabla)
                codigo_intermedio = generador.generar() 
                
                self.salida_codigo.insert(tk.END, "--- DIRECTIVAS (DATOS) ---\n\n")
                self.salida_codigo.insert(tk.END, codigo_intermedio)
            else:
                self.salida_codigo.insert(tk.END, "Corrige los errores semánticos primero:\n")
                for e in errores: 
                    self.salida_codigo.insert(tk.END, f"- {e}\n")
                    
        except Exception as e:
            # Si hay algún error en las clases, lo mostrará en el cuarto panel
            self.salida_codigo.insert(tk.END, f"¡Error detectado!\n{str(e)}")
            self.salida_scanner.insert(tk.END, f"\nError: {e}")