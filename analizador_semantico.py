# ==========================================
# Archivo: analizador_semantico.py
# ==========================================
from tabla_simbolos import TablaSimbolos

class AnalizadorSemantico:
    def __init__(self):
        self.tabla_simbolos = TablaSimbolos()
        self.errores = []

    def analizar(self, arbol_ast):
        for instruccion in arbol_ast:
            # 1. Dar de alta en la tabla de símbolos las variables de declaración[cite: 12]
            if instruccion['tipo_nodo'] == 'declaracion':
                tipo_dato = instruccion['tipo_dato']
                for var in instruccion['variables']:
                    try:
                        self.tabla_simbolos.agregar_simbolo(var, tipo_dato)
                    except Exception as e:
                        self.errores.append(str(e))
            
            # 2. Checar que los símbolos usados hayan sido declarados y checar tipos[cite: 12, 14]
            elif instruccion['tipo_nodo'] == 'asignacion':
                var_destino = instruccion['variable']
                try:
                    self.tabla_simbolos.checar_declaracion(var_destino)
                    
                    # Propagando los atributos en el árbol de expresión[cite: 13]
                    expr = instruccion['arbol_expresion']
                    if expr['izq'].isalpha(): self.tabla_simbolos.checar_declaracion(expr['izq'])
                    if expr['der'].isalpha(): self.tabla_simbolos.checar_declaracion(expr['der'])
                    
                except Exception as e:
                    self.errores.append(str(e))
                    
        return self.errores, self.tabla_simbolos.obtener_tabla()