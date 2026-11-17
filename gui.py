# ==========================================
# Archivo: gui.py
# Interfaz con Letra Grande para Proyector y Doble Scroll
# ==========================================
import tkinter as tk
from tkinter import font as tkfont
from scanner import Scanner
from parser_sintactico import Parser
from analizador_semantico import AnalizadorSemantico
from generador_codigo import GeneradorCodigoIntermedio
from generador_objeto import GeneradorCodigoObjeto


class InterfazCompilador:
    def __init__(self, ventana_raiz):
        self.ventana = ventana_raiz
        self.ventana.title("LispScript - Compilador Completo")
        self.ventana.geometry("1360x850")
        self.ventana.configure(bg="#f4f4f4")

        # Tamaño inicial grande para proyector (puedes subirlo con el botón A+)
        self.tamano_codigo = 16
        self.fuente_codigo = tkfont.Font(family="Consolas", size=self.tamano_codigo, weight="bold")
        self.fuente_botones = tkfont.Font(family="Segoe UI", size=13, weight="bold")
        self.fuente_etiquetas = tkfont.Font(family="Segoe UI", size=14, weight="bold")
        self.fuente_alerta = tkfont.Font(family="Segoe UI", size=20, weight="bold")

        self.scanner = Scanner()
        self._construir_interfaz()

    def _crear_cuadro_con_scroll(self, padre, ancho, alto):
        """
        Crea un cuadro de texto con barra de scroll vertical y horizontal
        y desactiva el salto de línea automático (wrap='none') para no romper tablas.
        """
        marco = tk.Frame(padre, bg="#cccccc", bd=1, relief="solid")

        scroll_y = tk.Scrollbar(marco, orient="vertical")
        scroll_x = tk.Scrollbar(marco, orient="horizontal")

        texto = tk.Text(
            marco,
            width=ancho,
            height=alto,
            font=self.fuente_codigo,
            wrap="none",
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
            padx=8,
            pady=8
        )

        scroll_y.config(command=texto.yview)
        scroll_x.config(command=texto.xview)

        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        texto.pack(side="left", fill="both", expand=True)

        return marco, texto

    def _construir_interfaz(self):
        # Barra superior para controlar el tamaño de letra en vivo frente al proyector
        barra_zoom = tk.Frame(self.ventana, bg="#e2e8f0", padx=15, pady=6)
        barra_zoom.pack(fill="x", side="top")

        tk.Label(
            barra_zoom, text="Tamaño de Letra (Proyector):",
            bg="#e2e8f0", font=("Segoe UI", 12, "bold")
        ).pack(side="left", padx=(0, 10))

        tk.Button(
            barra_zoom, text="A+ (Más Grande)", font=("Segoe UI", 11, "bold"),
            bg="#ffffff", command=self.aumentar_letra
        ).pack(side="left", padx=5)

        tk.Button(
            barra_zoom, text="A- (Más Pequeña)", font=("Segoe UI", 11, "bold"),
            bg="#ffffff", command=self.reducir_letra
        ).pack(side="left", padx=5)

        self.lbl_zoom = tk.Label(
            barra_zoom, text=f"{self.tamano_codigo} pt",
            bg="#e2e8f0", font=("Segoe UI", 12, "bold"), fg="#005a9e"
        )
        self.lbl_zoom.pack(side="left", padx=10)

        # Canvas con Scroll General para toda la ventana
        self.canvas_general = tk.Canvas(self.ventana, bg="#f4f4f4", highlightthickness=0)
        scroll_ventana_y = tk.Scrollbar(self.ventana, orient="vertical", command=self.canvas_general.yview)
        scroll_ventana_x = tk.Scrollbar(self.ventana, orient="horizontal", command=self.canvas_general.xview)

        self.canvas_general.configure(
            yscrollcommand=scroll_ventana_y.set,
            xscrollcommand=scroll_ventana_x.set
        )

        scroll_ventana_y.pack(side="right", fill="y")
        scroll_ventana_x.pack(side="bottom", fill="x")
        self.canvas_general.pack(side="left", fill="both", expand=True)

        contenedor = tk.Frame(self.canvas_general, bg="#f4f4f4", padx=20, pady=15)
        self.canvas_window = self.canvas_general.create_window((0, 0), window=contenedor, anchor="nw")

        contenedor.bind(
            "<Configure>",
            lambda e: self.canvas_general.configure(scrollregion=self.canvas_general.bbox("all"))
        )

        # =========================================================
        # FILA SUPERIOR IZQUIERDA: Entrada "Programa:"
        # =========================================================
        frame_programa = tk.Frame(contenedor, bg="#f4f4f4")
        frame_programa.grid(row=0, column=0, padx=(0, 15), pady=5, sticky="nsew")

        tk.Label(
            frame_programa, text="Programa:", bg="#f4f4f4",
            font=self.fuente_etiquetas
        ).pack(anchor="w", pady=(0, 8))

        marco_prog, self.entrada_texto = self._crear_cuadro_con_scroll(frame_programa, ancho=28, alto=11)
        marco_prog.pack(fill="both", expand=True)

        codigo_inicial = (
            "int x;\n"
            "int y;\n"
            "float res;\n"
            "x = 10 @ 2;"
        )
        self.entrada_texto.insert(tk.END, codigo_inicial)

        # =========================================================
        # FILA SUPERIOR CENTRAL: Botones (Tokens, Parser, Semantico)
        # =========================================================
        frame_central = tk.Frame(contenedor, bg="#f4f4f4")
        frame_central.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")

        frame_botones_sup = tk.Frame(frame_central, bg="#f4f4f4")
        frame_botones_sup.pack(anchor="w", pady=(0, 8))

        tk.Button(
            frame_botones_sup, text="Tokens", width=10, font=self.fuente_botones,
            command=self.ejecutar_tokens
        ).grid(row=0, column=0, padx=(0, 8))

        tk.Button(
            frame_botones_sup, text="Parser", width=10, font=self.fuente_botones,
            command=self.ejecutar_parser
        ).grid(row=0, column=1, padx=8)

        tk.Button(
            frame_botones_sup, text="Semantico", width=10, font=self.fuente_botones,
            command=self.ejecutar_semantico
        ).grid(row=0, column=2, padx=(8, 0))

        marco_central, self.salida_central = self._crear_cuadro_con_scroll(frame_central, ancho=38, alto=11)
        marco_central.pack(fill="both", expand=True)
        self._configurar_colores_texto(self.salida_central)

        # =========================================================
        # FILA SUPERIOR DERECHA: Alerta Grande (VERDE / ROJO)
        # =========================================================
        frame_estado = tk.Frame(contenedor, bg="#f4f4f4", width=280)
        frame_estado.grid(row=0, column=2, padx=(15, 0), pady=5, sticky="nw")

        self.lbl_estado = tk.Label(
            frame_estado, text="", bg="#f4f4f4",
            font=self.fuente_alerta, wraplength=280, justify="left"
        )
        self.lbl_estado.pack(anchor="nw", pady=10)

        # =========================================================
        # FILA INFERIOR IZQUIERDA: Botón "CI" y Tabla Ensamblador
        # =========================================================
        frame_ci = tk.Frame(contenedor, bg="#f4f4f4")
        frame_ci.grid(row=1, column=0, padx=(0, 15), pady=(20, 10), sticky="nsew")

        tk.Button(
            frame_ci, text="CI", width=10, font=self.fuente_botones,
            command=self.ejecutar_ci
        ).pack(anchor="w", pady=(0, 8))

        marco_ci, self.salida_ci = self._crear_cuadro_con_scroll(frame_ci, ancho=34, alto=13)
        marco_ci.pack(fill="both", expand=True)
        self._configurar_colores_texto(self.salida_ci)

        # =========================================================
        # FILA INFERIOR DERECHA: UN BOTÓN "CO" y Tabla Código Objeto
        # =========================================================
        frame_co = tk.Frame(contenedor, bg="#f4f4f4")
        frame_co.grid(row=1, column=1, columnspan=2, padx=(10, 0), pady=(20, 10), sticky="nsew")

        tk.Button(
            frame_co, text="CO", width=10, font=self.fuente_botones,
            command=self.ejecutar_co
        ).pack(anchor="w", pady=(0, 8))

        marco_co, self.salida_co = self._crear_cuadro_con_scroll(frame_co, ancho=62, alto=13)
        marco_co.pack(fill="both", expand=True)
        self._configurar_colores_texto(self.salida_co)

        # Pesos de expansión
        contenedor.grid_columnconfigure(0, weight=1)
        contenedor.grid_columnconfigure(1, weight=2)
        contenedor.grid_columnconfigure(2, weight=1)
        contenedor.grid_rowconfigure(0, weight=1)
        contenedor.grid_rowconfigure(1, weight=1)

    def aumentar_letra(self):
        if self.tamano_codigo < 32:
            self.tamano_codigo += 2
            self.fuente_codigo.configure(size=self.tamano_codigo)
            self.lbl_zoom.config(text=f"{self.tamano_codigo} pt")

    def reducir_letra(self):
        if self.tamano_codigo > 10:
            self.tamano_codigo -= 2
            self.fuente_codigo.configure(size=self.tamano_codigo)
            self.lbl_zoom.config(text=f"{self.tamano_codigo} pt")

    def _configurar_colores_texto(self, widget):
        widget.tag_config("exito", foreground="#15803d")  # Verde
        widget.tag_config("error", foreground="#dc2626")  # Rojo
        widget.tag_config("normal", foreground="#000000")

    def _mostrar_alerta(self, es_correcto, mensaje="CORRECTO"):
        if es_correcto:
            self.lbl_estado.config(text=mensaje, fg="#15803d")
        else:
            self.lbl_estado.config(text=mensaje, fg="#dc2626")

    # ---------------------------------------------------------
    # 1. BOTÓN TOKENS
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
    # 2. BOTÓN PARSER
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
    # 3. BOTÓN SEMANTICO
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
    # 4. BOTÓN CI (Código Intermedio)
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

    # ---------------------------------------------------------
    # 5. BOTÓN CO (Código Objeto - Binario y Hex)
    # ---------------------------------------------------------
    def ejecutar_co(self):
        codigo = self.entrada_texto.get("1.0", tk.END).strip()
        self.salida_co.delete("1.0", tk.END)
        try:
            tokens = self.scanner.analizar(codigo)
            parser = Parser(tokens)
            arbol_ast = parser.analizar()
            semantico = AnalizadorSemantico()
            errores, tabla = semantico.analizar(arbol_ast)

            if errores:
                self.salida_co.insert(tk.END, "No se puede generar CO por errores semánticos:\n\n", "error")
                for err in errores:
                    self.salida_co.insert(tk.END, f"- {err}\n", "error")
                self._mostrar_alerta(False, f"ERROR EN CO:\n{errores[0]}")
            else:
                generador_obj = GeneradorCodigoObjeto(tabla)
                codigo_co = generador_obj.generar(arbol_ast)
                self.salida_co.insert(tk.END, codigo_co + "\n", "normal")
                self._mostrar_alerta(True, "CORRECTO")
        except Exception as e:
            self.salida_co.insert(tk.END, f"¡ERROR AL GENERAR CO!\n{e}\n", "error")
            self._mostrar_alerta(False, f"ERROR EN CO:\n{e}")