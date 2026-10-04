# ==========================================
# Archivo: parser_sintactico.py
# ==========================================
from config_tokens import TOKEN_CODES

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.token_actual = self.tokens[self.pos] if self.tokens else None

    def avanzar(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.token_actual = self.tokens[self.pos]

    def match(self, codigo_esperado):
        if self.token_actual and self.token_actual['codigo'] == codigo_esperado:
            valor = self.token_actual['lexema']
            self.avanzar()
            return valor
        raise SyntaxError(f"Se esperaba token código {codigo_esperado} pero se encontró '{self.token_actual['lexema']}'.")

    def parse_Programa(self):
        instrucciones = []
# Agrega TOKEN_CODES['CHAR'] y TOKEN_CODES['STRING'] a las validaciones:
        while self.token_actual['codigo'] in [TOKEN_CODES['INT'], TOKEN_CODES['FLOAT'], TOKEN_CODES['CHAR'], TOKEN_CODES['STRING'], TOKEN_CODES['ID']]:
            if self.token_actual['codigo'] in [TOKEN_CODES['INT'], TOKEN_CODES['FLOAT'], TOKEN_CODES['CHAR'], TOKEN_CODES['STRING']]:
                instrucciones.append(self.parse_Declaracion())
            elif self.token_actual['codigo'] == TOKEN_CODES['ID']:
                instrucciones.append(self.parse_Asignacion())
        return instrucciones

    def parse_Declaracion(self):
        # int a, b, c ; | float d ;
        tipo = self.token_actual['lexema']
        self.avanzar()
        variables = []
        variables.append(self.match(TOKEN_CODES['ID']))
        
        while self.token_actual['codigo'] == TOKEN_CODES['COMA']:
            self.avanzar()
            variables.append(self.match(TOKEN_CODES['ID']))
            
        self.match(TOKEN_CODES['PUNTO_COMA'])
        return {'tipo_nodo': 'declaracion', 'tipo_dato': tipo, 'variables': variables}

    def parse_Asignacion(self):
        # id = id @ id ;
        variable = self.match(TOKEN_CODES['ID'])
        self.match(TOKEN_CODES['ASIGNACION'])
        expresion_izq = self.token_actual['lexema']
        self.avanzar() # Simplificado para avanzar el primer factor
        operador = self.token_actual['lexema']
        self.avanzar() # Avanza operador
        expresion_der = self.token_actual['lexema']
        self.avanzar() # Avanza segundo factor
        self.match(TOKEN_CODES['PUNTO_COMA'])
        
        return {
            'tipo_nodo': 'asignacion', 
            'variable': variable, 
            'arbol_expresion': {'izq': expresion_izq, 'op': operador, 'der': expresion_der}
        }

    def analizar(self):
        arbol_ast = self.parse_Programa()
        if self.token_actual['codigo'] != TOKEN_CODES['EOF']:
            raise SyntaxError(f"Código inesperado al final: '{self.token_actual['lexema']}'")
        return arbol_ast