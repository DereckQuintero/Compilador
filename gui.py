# ==========================================
# Archivo: gui.py
# ==========================================
import tkinter as tk
from tkinter import scrolledtext
from scanner import Scanner, ErrorLexico
from parser_sintactico import Parser
from analizador_semantico import AnalizadorSemantico

class InterfazCompilador:
    def __init__(self, ventana_raiz):
        self.ventana = ventana_raiz
        self.ventana.title("Compilador - Fases: Léxica, Sintáctica y Semántica")
        # Ventana más ancha para acomodar las 3 fases
        self.ventana.geometry("1100x650")
        
        self.scanner = Scanner()
        self._construir_interfaz()

    def _construir_interfaz(self):
        # Panel superior de entrada
        self.entrada_texto = scrolledtext.ScrolledText(self.ventana, width=120, height=8)
        self.entrada_texto.pack(pady=10)
        self.entrada_texto.insert(tk.END, "int a, b, c;\nfloat d;\na = b @ c;")

        tk.Button(self.ventana, text="Analizar Código", bg="#4CAF50", fg="white", 
                  font=("Arial", 10, "bold"), command=self.ejecutar_analisis).pack(pady=5)

        # Contenedor para los 3 paneles de salida
        panel_inferior = tk.Frame(self.ventana)
        panel_inferior.pack(fill="both", expand=True, padx=10, pady=10)

        # 1. Panel del Scanner (Análisis Léxico)
        self.salida_scanner = scrolledtext.ScrolledText(panel_inferior, width=30, height=20)
        self.salida_scanner.pack(side="left", fill="both", expand=True, padx=5)
        
        # 2. Panel del Parser (Análisis Sintáctico / AST)
        self.salida_parser = scrolledtext.ScrolledText(panel_inferior, width=35, height=20)
        self.salida_parser.pack(side="left", fill="both", expand=True, padx=5)
        
        # 3. Panel del Semántico (Tabla de Símbolos)
        self.salida_semantico = scrolledtext.ScrolledText(panel_inferior, width=35, height=20)
        self.salida_semantico.pack(side="left", fill="both", expand=True, padx=5)

    def ejecutar_analisis(self):
        codigo = self.entrada_texto.get("1.0", tk.END).strip()
        
        # Limpiar pantallas
        self.salida_scanner.delete("1.0", tk.END)
        self.salida_parser.delete("1.0", tk.END)
        self.salida_semantico.delete("1.0", tk.END)
        
        try:
            # --- FASE 1: SCANNER ---
            tokens = self.scanner.analizar(codigo)
            self.salida_scanner.insert(tk.END, "--- ANÁLISIS LÉXICO ---\n")
            for t in tokens:
                self.salida_scanner.insert(tk.END, f"{t['lexema']} -> {t['tipo']} ({t['codigo']})\n")

            # --- FASE 2: PARSER ---
            parser = Parser(tokens)
            arbol_ast = parser.analizar()
            self.salida_parser.insert(tk.END, "--- ÁRBOL AST (SINTÁCTICO) ---\n")
            for nodo in arbol_ast:
                self.salida_parser.insert(tk.END, f"{nodo}\n\n")

            # --- FASE 3: SEMÁNTICO ---
            semantico = AnalizadorSemantico()
            errores, tabla = semantico.analizar(arbol_ast)
            
            self.salida_semantico.insert(tk.END, "--- ANÁLISIS SEMÁNTICO ---\n\n")
            if errores:
                self.salida_semantico.insert(tk.END, "¡ERRORES ENCONTRADOS!\n")
                for e in errores: 
                    self.salida_semantico.insert(tk.END, f"- {e}\n")
            else:
                self.salida_semantico.insert(tk.END, "Análisis sin errores.\n\n")
                
            self.salida_semantico.insert(tk.END, "--- TABLA DE SÍMBOLOS ---\n")
            self.salida_semantico.insert(tk.END, "Nombre\tTipo\tDirección\n")
            self.salida_semantico.insert(tk.END, "-"*30 + "\n")
            for nombre, info in tabla.items():
                self.salida_semantico.insert(tk.END, f"{nombre}\t{info['tipo']}\t{info['direccion']}\n")
                    
        except Exception as e:
            self.salida_scanner.insert(tk.END, f"\nError en el flujo:\n{e}")