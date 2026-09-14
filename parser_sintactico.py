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
            self.avanzar()
        else:
            esperado = [k for k, v in TOKEN_CODES.items() if v == codigo_esperado][0]
            encontrado = self.token_actual['lexema'] if self.token_actual else 'Nada'
            raise SyntaxError(f"Se esperaba '{esperado}' pero se encontró '{encontrado}'.")

    def parse_Programa(self):
        # Programa -> Sentencia Programa | cadena vacía
        while self.token_actual['codigo'] in [TOKEN_CODES['ID'], TOKEN_CODES['IF']]:
            self.parse_Sentencia()

    def parse_Sentencia(self):
        # Sentencia -> Asignacion | EstructuraIf
        if self.token_actual['codigo'] == TOKEN_CODES['ID']:
            self.parse_Asignacion()
        elif self.token_actual['codigo'] == TOKEN_CODES['IF']:
            self.parse_EstructuraIf()
        else:
            raise SyntaxError(f"Instrucción no válida iniciando con '{self.token_actual['lexema']}'")

    def parse_Asignacion(self):
        # Asignacion -> Id = E ;
        self.match(TOKEN_CODES['ID'])
        self.match(TOKEN_CODES['ASIGNACION'])
        self.parse_E()
        self.match(TOKEN_CODES['PUNTO_COMA'])

    def parse_EstructuraIf(self):
        # EstructuraIf -> if ( Condicion ) { Programa }
        self.match(TOKEN_CODES['IF'])
        self.match(TOKEN_CODES['PAR_ABRE'])
        self.parse_Condicion()
        self.match(TOKEN_CODES['PAR_CIERRA'])
        self.match(TOKEN_CODES['LLAVE_ABRE'])
        self.parse_Programa()
        self.match(TOKEN_CODES['LLAVE_CIERRA'])

    def parse_Condicion(self):
        # Condicion -> E OpRel E
        self.parse_E()
        self.match(TOKEN_CODES['OP_REL'])
        self.parse_E()

    def parse_E(self):
        # Expresión Aritmética (Maneja sumas @ y restas #)
        self.parse_T()
        while self.token_actual['codigo'] in [TOKEN_CODES['OP_SUMA'], TOKEN_CODES['OP_RESTA']]:
            self.avanzar() # Consumimos el operador
            self.parse_T()

    def parse_T(self):
        # Términos (Maneja multiplicaciones == y divisiones &)
        self.parse_F()
        while self.token_actual['codigo'] in [TOKEN_CODES['OP_IGUAL_MULT'], TOKEN_CODES['OP_DIV']]:
            self.avanzar() # Consumimos el operador
            self.parse_F()

    def parse_F(self):
        # Factores: ID, NUM, o ( E )
        if self.token_actual['codigo'] == TOKEN_CODES['ID']:
            self.match(TOKEN_CODES['ID'])
        elif self.token_actual['codigo'] == TOKEN_CODES['NUM']:
            self.match(TOKEN_CODES['NUM'])
        elif self.token_actual['codigo'] == TOKEN_CODES['PAR_ABRE']:
            self.match(TOKEN_CODES['PAR_ABRE'])
            self.parse_E()
            self.match(TOKEN_CODES['PAR_CIERRA'])
        else:
            raise SyntaxError(f"Se esperaba un número, variable o '(' pero se encontró '{self.token_actual['lexema']}'.")

    def analizar(self):
        try:
            self.parse_Programa()
            if self.token_actual['codigo'] != TOKEN_CODES['EOF']:
                raise SyntaxError(f"Código inesperado al final: '{self.token_actual['lexema']}'")
            return True, "Programa Sintácticamente OK"
        except SyntaxError as e:
            return False, f"Syntax Error! {str(e)}"