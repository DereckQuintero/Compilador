# ==========================================
# Archivo: gui.py
# Interfaz Gráfica con Botones Independientes y Panel CI Amplio
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
        self.ventana.title("LispScript - Compilador")
        self.ventana.geometry("1150x780")
        self.ventana.configure(bg="#f4f4f4")

        self.scanner = Scanner()
        self._construir_interfaz()

    def _construir_interfaz(self):
        # Contenedor principal con Grid
        contenedor = tk.Frame(self.ventana, bg="#f4f4f4", padx=20, pady=15)
        contenedor.pack(fill="both", expand=True)

        # =========================================================
        # SECCIÓN SUPERIOR IZQUIERDA: Entrada "Programa:"
        # =========================================================
        frame_programa = tk.Frame(contenedor, bg="#f4f4f4")
        frame_programa.grid(row=0, column=0, padx=(0, 25), pady=5, sticky="nsew")

        tk.Label(
            frame_programa, text="Programa:", bg="#f4f4f4",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", pady=(0, 8))

        self.entrada_texto = scrolledtext.ScrolledText(
            frame_programa, width=38, height=16, font=("Consolas", 11)
        )
        self.entrada_texto.pack(fill="both", expand=True)

        # Código de prueba inicial
        codigo_inicial = (
            "int x;\n"
            "int y;\n"
            "float res;\n"
            "x = 10 @ 2;"
        )
        self.entrada_texto.insert(tk.END, codigo_inicial)

        # =========================================================
        # SECCIÓN SUPERIOR CENTRAL: Botones (Tokens, Parser, Semantico)
        # =========================================================
        frame_central = tk.Frame(contenedor, bg="#f4f4f4")
        frame_central.grid(row=0, column=1, padx=15, pady=5, sticky="nsew")

        frame_botones_sup = tk.Frame(frame_central, bg="#f4f4f4")
        frame_botones_sup.pack(anchor="w", pady=(0, 8))

        tk.Button(
            frame_botones_sup, text="Tokens", width=11, font=("Segoe UI", 10, "bold"),
            command=self.ejecutar_tokens
        ).grid(row=0, column=0, padx=(0, 8))

        tk.Button(
            frame_botones_sup, text="Parser", width=11, font=("Segoe UI", 10, "bold"),
            command=self.ejecutar_parser
        ).grid(row=0, column=1, padx=8)

        tk.Button(
            frame_botones_sup, text="Semantico", width=11, font=("Segoe UI", 10, "bold"),
            command=self.ejecutar_semantico
        ).grid(row=0, column=2, padx=(8, 0))

        self.salida_central = scrolledtext.ScrolledText(
            frame_central, width=48, height=16, font=("Consolas", 10)
        )
        self.salida_central.pack(fill="both", expand=True)
        self._configurar_colores_texto(self.salida_central)

        # =========================================================
        # SECCIÓN SUPERIOR DERECHA: Alerta (VERDE / ROJO)
        # =========================================================
        frame_estado = tk.Frame(contenedor, bg="#f4f4f4", width=260)
        frame_estado.grid(row=0, column=2, padx=(20, 0), pady=5, sticky="nw")

        self.lbl_estado = tk.Label(
            frame_estado, text="", bg="#f4f4f4",
            font=("Segoe UI", 16, "bold"), wraplength=250, justify="left"
        )
        self.lbl_estado.pack(anchor="nw", pady=5)

        # =========================================================
        # SECCIÓN INFERIOR: Botón "CI" y Cuadro Amplio para la Tabla
        # =========================================================
        frame_ci = tk.Frame(contenedor, bg="#f4f4f4")
        frame_ci.grid(row=1, column=0, columnspan=2, pady=(20, 0), sticky="nsew")

        tk.Button(
            frame_ci, text="CI", width=10, font=("Segoe UI", 10, "bold"),
            command=self.ejecutar_ci
        ).pack(anchor="w", pady=(0, 8))

        # Cuadro más amplio para que las 3 columnas de ensamblador tengan buen espacio
        self.salida_ci = scrolledtext.ScrolledText(
            frame_ci, width=90, height=15, font=("Consolas", 11)
        )
        self.salida_ci.pack(fill="both", expand=True)
        self._configurar_colores_texto(self.salida_ci)

        # Pesos de expansión
        contenedor.grid_columnconfigure(0, weight=1)
        contenedor.grid_columnconfigure(1, weight=1)
        contenedor.grid_columnconfigure(2, weight=1)
        contenedor.grid_rowconfigure(0, weight=1)
        contenedor.grid_rowconfigure(1, weight=1)

    def _configurar_colores_texto(self, widget):
        widget.tag_config("exito", foreground="#15803d")  # Verde
        widget.tag_config("error", foreground="#dc2626")  # Rojo
        widget.tag_config("normal", foreground="#000000")

    def _mostrar_alerta(self, es_correcto, mensaje="CORRECTO"):
        if es_correcto:
            self.lbl_estado.config(text=mensaje, fg="#15803d")  # Verde
        else:
            self.lbl_estado.config(text=mensaje, fg="#dc2626")  # Rojo

    # ---------------------------------------------------------
    # 1. BOTÓN TOKENS (Solo ejecuta el Scanner)
    # ---------------------------------------------------------
    def ejecutar_tokens(self):
        codigo = self.entrada_texto.get("1.0", tk.END).strip()
        self.salida_central.delete("1.0", tk.END)

        try:
            tokens = self.scanner.analizar(codigo)
            self.salida_central.insert(tk.END, "--- TOKENS GENERADOS ---\n\n", "exito")
            for t in tokens:
                if isinstance(t, dict):
                    self.salida_central.insert(tk.END, f"{t['lexema']} -> {t['tipo']}\n", "normal")
                else:
                    self.salida_central.insert(tk.END, f"<{t[0]}, {t[1]}>\n", "normal")

            self._mostrar_alerta(True, "CORRECTO")
        except Exception as e:
            self.salida_central.insert(tk.END, f"¡ERROR LÉXICO!\n{e}\n", "error")
            self._mostrar_alerta(False, f"ERROR LÉXICO:\n{e}")

    # ---------------------------------------------------------
    # 2. BOTÓN PARSER (Ejecuta el Análisis Sintáctico)
    # ---------------------------------------------------------
    def ejecutar_parser(self):
        codigo = self.entrada_texto.get("1.0", tk.END).strip()
        self.salida_central.delete("1.0", tk.END)

        try:
            tokens = self.scanner.analizar(codigo)
            parser = Parser(tokens)
            arbol_ast = parser.analizar()

            self.salida_central.insert(tk.END, "--- ÁRBOL SINTÁCTICO (AST) ---\n\n", "exito")
            for nodo in arbol_ast:
                self.salida_central.insert(tk.END, f"{nodo}\n\n", "normal")

            self._mostrar_alerta(True, "CORRECTO")
        except Exception as e:
            self.salida_central.insert(tk.END, f"¡ERROR SINTÁCTICO!\n{e}\n", "error")
            self._mostrar_alerta(False, f"ERROR SINTÁCTICO:\n{e}")

    # ---------------------------------------------------------
    # 3. BOTÓN SEMÁNTICO (Ejecuta Tabla de Símbolos y Validaciones)
    # ---------------------------------------------------------
    def ejecutar_semantico(self):
        codigo = self.entrada_texto.get("1.0", tk.END).strip()
        self.salida_central.delete("1.0", tk.END)

        try:
            tokens = self.scanner.analizar(codigo)
            parser = Parser(tokens)
            arbol_ast = parser.analizar()

            semantico = AnalizadorSemantico()
            errores, tabla = semantico.analizar(arbol_ast)

            if errores:
                self.salida_central.insert(tk.END, "¡ERRORES SEMÁNTICOS DETECTADOS!\n\n", "error")
                for err in errores:
                    self.salida_central.insert(tk.END, f"- {err}\n", "error")
                self._mostrar_alerta(False, f"ERROR SEMÁNTICO:\n{errores[0]}")
            else:
                self.salida_central.insert(tk.END, "--- TABLA DE SÍMBOLOS (TS) ---\n", "exito")
                self.salida_central.insert(tk.END, f"{'Nombre':<12}{'Tipo':<10}{'Memoria':<12}{'Directiva'}\n", "normal")
                self.salida_central.insert(tk.END, "-" * 48 + "\n", "normal")
                for nombre, info in tabla.items():
                    self.salida_central.insert(
                        tk.END,
                        f"{nombre:<12}{info['tipo']:<10}{info['direccion']:<12}{info.get('directiva', '')}\n",
                        "normal"
                    )
                self._mostrar_alerta(True, "CORRECTO")
        except Exception as e:
            self.salida_central.insert(tk.END, f"¡ERROR EN ANÁLISIS SEMÁNTICO!\n{e}\n", "error")
            self._mostrar_alerta(False, f"ERROR:\n{e}")

    # ---------------------------------------------------------
    # 4. BOTÓN CI (Genera el Código Intermedio .486 espaciado)
    # ---------------------------------------------------------
    def ejecutar_ci(self):
        codigo = self.entrada_texto.get("1.0", tk.END).strip()
        self.salida_ci.delete("1.0", tk.END)

        try:
            tokens = self.scanner.analizar(codigo)
            parser = Parser(tokens)
            arbol_ast = parser.analizar()

            semantico = AnalizadorSemantico()
            errores, tabla = semantico.analizar(arbol_ast)

            if errores:
                self.salida_ci.insert(tk.END, "No se puede generar CI por errores semánticos:\n\n", "error")
                for err in errores:
                    self.salida_ci.insert(tk.END, f"- {err}\n", "error")
                self._mostrar_alerta(False, f"ERROR EN CI:\n{errores[0]}")
            else:
                generador = GeneradorCodigoIntermedio(tabla)
                codigo_ci = generador.generar(arbol_ast)
                self.salida_ci.insert(tk.END, codigo_ci + "\n", "normal")
                self._mostrar_alerta(True, "CORRECTO")
        except Exception as e:
            self.salida_ci.insert(tk.END, f"¡ERROR AL GENERAR CI!\n{e}\n", "error")
            self._mostrar_alerta(False, f"ERROR EN CI:\n{e}")