# ==========================================
# Archivo: tabla_simbolos.py
# ==========================================
class TablaSimbolos:
    def __init__(self):
        self.simbolos = {}
        self.offset_actual = 0x0000  # Iniciamos en el offset 0000[cite: 16]
        self.segmento = "001E"       # Segmento fijo según apuntes del pizarrón[cite: 16]

    def agregar_simbolo(self, nombre, tipo):
        if nombre in self.simbolos:
            raise Exception(f"Variable '{nombre}' ya ha sido declarada.")
        
        # Determinar el tamaño en memoria y la directiva Intel
        if tipo == 'int':
            size = 2
            directiva = 'DW'        # Define Word (16 bits)
        elif tipo == 'float':
            size = 4
            directiva = 'DD'        # Define Double (32 bits)
        elif tipo == 'char':
            size = 1
            directiva = 'DB'        # Define Byte (8 bits)
        elif tipo == 'string':
            size = 80               # 80 bytes según diferencia 0009 a 0059[cite: 16]
            directiva = 'DB 80 DUP(?)' # Arreglo de 80 bytes
        else:
            size = 2
            directiva = 'DW'

        # Formatear la dirección como 001E:OFFSET (en Hexadecimal mayúscula)[cite: 16, 17]
        direccion_hex = f"{self.segmento}:{self.offset_actual:04X}"
        
        self.simbolos[nombre] = {
            'tipo': tipo, 
            'direccion': direccion_hex,
            'size': size,
            'directiva': directiva
        }
        
        # Aumentar el offset para la siguiente variable
        self.offset_actual += size

    def checar_declaracion(self, nombre):
        if nombre not in self.simbolos:
            raise Exception(f"Variable '{nombre}' no declarada.")
        return self.simbolos[nombre]['tipo']

    def obtener_tabla(self):
        return self.simbolos


    