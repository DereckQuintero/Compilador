# ==========================================
# Archivo: tabla_simbolos.py
# ==========================================
class TablaSimbolos:
    def __init__(self):
        self.simbolos = {}
        self.siguiente_direccion = 0  # Empezamos en la dirección 0

    def agregar_simbolo(self, nombre, tipo):
        # 1. Checar que no haya declaraciones múltiples[cite: 14]
        if nombre in self.simbolos:
            raise Exception(f"Variable '{nombre}' ya ha sido declarada previamente.")
        
        # 2. Registrar en la tabla con su dirección[cite: 15]
        direccion = self.siguiente_direccion
        self.simbolos[nombre] = {'tipo': tipo, 'direccion': direccion}
        
        # 3. Calcular memoria: int = 16 bits (2 bytes), float = 32 bits (4 bytes)[cite: 16]
        if tipo == 'int':
            self.siguiente_direccion += 2
        elif tipo == 'float':
            self.siguiente_direccion += 4

    def checar_declaracion(self, nombre):
        # Asegurar que no se usan identificadores no declarados[cite: 14]
        if nombre not in self.simbolos:
            raise Exception(f"Variable '{nombre}' no declarada.")
        return self.simbolos[nombre]['tipo']

    def obtener_tabla(self):
        return self.simbolos