# ==========================================
# Generación de Código Intermedio (CI - .486 / 8086)
# ==========================================

class GeneradorCodigoIntermedio:
    def __init__(self, tabla_simbolos):
        self.tabla = tabla_simbolos

    def _fila(self, col1="", col2="", col3=""):
        """
        Columna 1: Variables / Etiquetas (16 espacios)
        Columna 2: Directivas / Instrucciones (16 espacios)
        Columna 3: Operadores/ Valores
        """
        return f"{col1:<16}{col2:<16}{col3}".rstrip()

    def generar(self, arbol_ast=None):
        lineas = []

        # --- ENCABEZADO DEL ENSAMBLADOR (.486 / 8086) ---
        lineas.append(self._fila("", "TITLE", "Prac01"))
        lineas.append(self._fila("", ".MODEL", "Small"))
        lineas.append(self._fila("", ".486", ""))
        lineas.append(self._fila("", ".STACK", ""))
        lineas.append(self._fila("", ".DATA", ""))

        # --- SEGMENTO DE DATOS (Variables de la Tabla de Simbolos) ---
        for nombre, info in self.tabla.items():
            directiva = info.get('directiva', 'DW')
            if directiva == 'DB 80 DUP(?)':
                lineas.append(self._fila(nombre, "DB", "80 DUP(?)"))
            else:
                lineas.append(self._fila(nombre, directiva, "?"))

        # --- SEGMENTO DE CODIGO ---
        lineas.append(self._fila("", ".CODE", ""))
        lineas.append(self._fila("MAIN", "PROC", "FAR"))
        lineas.append(self._fila("", ".STARTUP", ""))

        # --- TRADUCCION DE INSTRUCCIONES DEL PROGRAMA ---
        if arbol_ast:
            for nodo in arbol_ast:
                if isinstance(nodo, dict) and nodo.get('tipo_nodo') == 'asignacion':
                    var_dest = nodo.get('variable', '')
                    expr = nodo.get('arbol_expresion')

                    # Si es una operación binaria (ej. x = 10 @ 2; o A = B @ diam;)
                    if isinstance(expr, dict) and 'op' in expr:
                        izq = expr.get('izq', '')
                        op = expr.get('op', '')
                        der = expr.get('der', '')

                        lineas.append(self._fila("", "MOV", f"AX, {izq}"))
                        if op == '@':
                            lineas.append(self._fila("", "ADD", f"AX, {der}"))
                        elif op == '#':
                            lineas.append(self._fila("", "SUB", f"AX, {der}"))
                        elif op == '==':
                            lineas.append(self._fila("", "MOV", f"BX, {der}"))
                            lineas.append(self._fila("", "MUL", "BX"))
                        elif op == '&':
                            lineas.append(self._fila("", "MOV", f"BX, {der}"))
                            lineas.append(self._fila("", "DIV", "BX"))
                        lineas.append(self._fila("", "MOV", f"{var_dest}, AX"))
                    else:
                        # Asignacion directa como en el pizarron: MOV x, 5
                        lineas.append(self._fila("", "MOV", f"{var_dest}, {expr}"))

        # --- CIERRE DEL PROGRAMA ---
        lineas.append(self._fila("", ".EXIT", ""))
        lineas.append(self._fila("MAIN", "ENDP", ""))
        lineas.append(self._fila("", "END", ""))

        return "\n".join(lineas)
    