# ==========================================
# Archivo: generador_objeto.py
# Fase: Generación de Código Objeto (CO - Binario y Hexadecimal 8086)
# ==========================================

class GeneradorCodigoObjeto:
    def __init__(self, tabla_simbolos):
        self.tabla = tabla_simbolos
        self.offsets_vars = {}

    def _bin16(self, valor):
        """Convierte un entero a binario de 16 bits separado en bloques de 4 bits."""
        b = f"{valor & 0xFFFF:016b}"
        return f"{b[0:4]} {b[4:8]} {b[8:12]} {b[12:16]}"

    def _bin8(self, valor):
        """Convierte un entero a binario de 8 bits separado en bloques de 4 bits."""
        b = f"{valor & 0xFF:08b}"
        return f"{b[0:4]} {b[4:8]}"

    def _fila(self, seccion, dir_bin, contenido_bin, valor_hex):
        """Formatea cada fila respetando las columnas DIR | CONTENIDO | HEX del pizarrón."""
        return f"{seccion:<9} {dir_bin:<21} | {contenido_bin:<42} | {valor_hex}"

    def generar(self, arbol_ast=None):
        lineas = []

        # Encabezado de la tabla igual al pizarrón
        encabezado = f"{'SECCIÓN':<9} {'DIR':<21} | {'CONTENIDO':<42} | {'HEX'}"
        separador_sup = "=" * 92
        separador_medio = "-" * 92

        lineas.append(encabezado)
        lineas.append(separador_sup)

        # =========================================================
        # 1. SECCIÓN DATOS (Inicia en 0000 0000 0000 0000)
        # =========================================================
        offset_datos = 0
        primera_fila_datos = True

        if not self.tabla:
            lineas.append(self._fila("DATOS", self._bin16(0), "0000 0000 0000 0000", "0000H"))
        else:
            for nombre, info in self.tabla.items():
                self.offsets_vars[nombre] = offset_datos
                tipo = info.get('tipo', 'int')
                etiqueta = "DATOS" if primera_fila_datos else ""
                primera_fila_datos = False

                dir_bin = self._bin16(offset_datos)

                if tipo == 'int':
                    # DW (2 bytes = 16 bits)
                    lineas.append(self._fila(etiqueta, dir_bin, "0000 0000 0000 0000", f"0000H ({nombre})"))
                    offset_datos += 2
                elif tipo == 'float':
                    # DD (4 bytes = 32 bits)
                    lineas.append(self._fila(etiqueta, dir_bin, "0000 0000 0000 0000  0000 0000 0000 0000", f"00000000H ({nombre})"))
                    offset_datos += 4
                elif tipo == 'char':
                    # DB (1 byte = 8 bits)
                    lineas.append(self._fila(etiqueta, dir_bin, "0000 0000", f"00H ({nombre})"))
                    offset_datos += 1
                elif tipo == 'string':
                    # DB 80 DUP(?) (80 bytes)
                    lineas.append(self._fila(etiqueta, dir_bin, "0000 0000 ... [80 Bytes reservados]", f"50H DUP(00H) ({nombre})"))
                    offset_datos += 80
                else:
                    lineas.append(self._fila(etiqueta, dir_bin, "0000 0000 0000 0000", f"0000H ({nombre})"))
                    offset_datos += 2

        # Línea punteada divisoria entre DATOS y CÓDIGO
        lineas.append(separador_medio)

        # =========================================================
        # 2. SECCIÓN CÓDIGO (Inicia en 0000 0000 0000 0000)
        # =========================================================
        offset_codigo = 0
        primera_fila_cod = True

        def agregar_instruccion(bin_str, hex_str, tamano_bytes):
            nonlocal offset_codigo, primera_fila_cod
            etiqueta = "CÓDIGO" if primera_fila_cod else ""
            primera_fila_cod = False
            lineas.append(self._fila(etiqueta, self._bin16(offset_codigo), bin_str, hex_str))
            offset_codigo += tamano_bytes

        if arbol_ast:
            for nodo in arbol_ast:
                if isinstance(nodo, dict) and nodo.get('tipo_nodo') == 'asignacion':
                    var_dest = nodo.get('variable', '')
                    dir_dest = self.offsets_vars.get(var_dest, 0)
                    expr = nodo.get('arbol_expresion')

                    # Caso A: Operación binaria (ej. x = 10 @ 2; o A = B @ valor;)
                    if isinstance(expr, dict) and 'op' in expr:
                        izq = str(expr.get('izq', '0'))
                        op = expr.get('op', '@')
                        der = str(expr.get('der', '0'))

                        # 1. Cargar operando izquierdo en AX (W=1, REG=000 -> AX)
                        if izq.isdigit():
                            val = int(izq)
                            # MOV AX, inm16 -> Opcode 1011 1000 (B8) + inm16 (3 bytes)
                            bin_ins = f"1011 1000  {self._bin16(val)}"
                            hex_ins = f"B8 {val:04X}H"
                            agregar_instruccion(bin_ins, hex_ins, 3)
                        else:
                            dir_izq = self.offsets_vars.get(izq, 0)
                            # MOV AX, [mem] -> 1000 1011 0000 0110 (8B 06) + dir (4 bytes)
                            bin_ins = f"1000 1011 0000 0110  {self._bin16(dir_izq)}"
                            hex_ins = f"8B 06 {dir_izq:04X}H"
                            agregar_instruccion(bin_ins, hex_ins, 4)

                        # 2. Aplicar operador (@, #, ==, &)
                        if op == '@':  # ADD AX
                            if der.isdigit():
                                val = int(der)
                                bin_ins = f"0000 0101  {self._bin16(val)}"
                                hex_ins = f"05 {val:04X}H"
                                agregar_instruccion(bin_ins, hex_ins, 3)
                            else:
                                dir_der = self.offsets_vars.get(der, 0)
                                bin_ins = f"0000 0011 0000 0110  {self._bin16(dir_der)}"
                                hex_ins = f"03 06 {dir_der:04X}H"
                                agregar_instruccion(bin_ins, hex_ins, 4)

                        elif op == '#':  # SUB AX
                            if der.isdigit():
                                val = int(der)
                                bin_ins = f"0010 1101  {self._bin16(val)}"
                                hex_ins = f"2D {val:04X}H"
                                agregar_instruccion(bin_ins, hex_ins, 3)
                            else:
                                dir_der = self.offsets_vars.get(der, 0)
                                bin_ins = f"0010 1011 0000 0110  {self._bin16(dir_der)}"
                                hex_ins = f"2B 06 {dir_der:04X}H"
                                agregar_instruccion(bin_ins, hex_ins, 4)

                        elif op in ('==', '&'):  # MUL BX o DIV BX (W=1, REG=011 -> BX)
                            if der.isdigit():
                                val = int(der)
                                # MOV BX, inm16 -> 1011 1011 (BB)
                                agregar_instruccion(f"1011 1011  {self._bin16(val)}", f"BB {val:04X}H", 3)
                            else:
                                dir_der = self.offsets_vars.get(der, 0)
                                # MOV BX, [mem] -> 1000 1011 0001 1110 (8B 1E)
                                agregar_instruccion(f"1000 1011 0001 1110  {self._bin16(dir_der)}", f"8B 1E {dir_der:04X}H", 4)

                            if op == '==':
                                # MUL BX -> 1111 0111 1110 0011 (F7 E3)
                                agregar_instruccion("1111 0111 1110 0011", "F7 E3H", 2)
                            else:
                                # DIV BX -> 1111 0111 1111 0011 (F7 F3)
                                agregar_instruccion("1111 0111 1111 0011", "F7 F3H", 2)

                        # 3. Guardar acumulador AX en variable destino: MOV [var_dest], AX -> 89 06 + dir
                        bin_ins = f"1000 1001 0000 0110  {self._bin16(dir_dest)}"
                        hex_ins = f"89 06 {dir_dest:04X}H"
                        agregar_instruccion(bin_ins, hex_ins, 4)

                    # Caso B: Asignación simple directa (ej. x = 5;)
                    else:
                        val_str = str(expr)
                        if val_str.isdigit():
                            val = int(val_str)
                            # MOV AX, inm16 (B8) y MOV [var_dest], AX (89 06)
                            agregar_instruccion(f"1011 1000  {self._bin16(val)}", f"B8 {val:04X}H", 3)
                            agregar_instruccion(f"1000 1001 0000 0110  {self._bin16(dir_dest)}", f"89 06 {dir_dest:04X}H", 4)
                        else:
                            dir_origen = self.offsets_vars.get(val_str, 0)
                            agregar_instruccion(f"1000 1011 0000 0110  {self._bin16(dir_origen)}", f"8B 06 {dir_origen:04X}H", 4)
                            agregar_instruccion(f"1000 1001 0000 0110  {self._bin16(dir_dest)}", f"89 06 {dir_dest:04X}H", 4)

        # Instrucciones de cierre (.EXIT -> MOV AH, 4CH + INT 21H)
        agregar_instruccion("1011 0100 0100 1100", "B4 4CH", 2)
        agregar_instruccion("1100 1101 0010 0001", "CD 21H", 2)

        return "\n".join(lineas)