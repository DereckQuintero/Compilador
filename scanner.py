# ==========================================
# Archivo: scanner.py
# ==========================================
import re
from config_tokens import TOKEN_CODES

class ErrorLexico(Exception):
    pass

class Scanner:
    def __init__(self):
        # Definición de tokens basados en la gramática
        self.especificacion_tokens = [
            ('IF',           r'\bif\b'),
            ('OP_IGUAL_MULT',r'=='),
            ('OP_SUMA',      r'@'),
            ('OP_RESTA',     r'#'),
            ('OP_DIV',       r'&'),
            ('ASIGNACION',   r'='),
            ('OP_REL',       r'[<>]'),
            ('PUNTO_COMA',   r';'),
            ('PAR_ABRE',     r'\('),
            ('PAR_CIERRA',   r'\)'),
            ('LLAVE_ABRE',   r'\{'),
            ('LLAVE_CIERRA', r'\}'),
            ('ID',           r'[A-Za-z][A-Za-z0-9]*'),
            ('NUM',          r'\d+'),
            ('ESPACIOS',     r'[ \t\n]+'),
            ('ERROR',        r'.'),
        ]
        self.regex_completa = '|'.join(f'(?P<{nombre}>{regex})' for nombre, regex in self.especificacion_tokens)

    def analizar(self, codigo_fuente):
        tokens_encontrados = []
        numero_linea = 1
        
        for coincidencia in re.finditer(self.regex_completa, codigo_fuente):
            tipo_token = coincidencia.lastgroup
            valor_token = coincidencia.group(tipo_token)
            
            if tipo_token == 'ESPACIOS':
                numero_linea += valor_token.count('\n')
                continue
            elif tipo_token == 'ERROR':
                raise ErrorLexico(f'Error Léxico en línea {numero_linea}: Carácter "{valor_token}"')
            else:
                # Agregamos el formato de tabla (lexema, tipo, codigo)
                tokens_encontrados.append({
                    'lexema': valor_token,
                    'tipo': tipo_token,
                    'codigo': TOKEN_CODES[tipo_token]
                })
                
        tokens_encontrados.append({'lexema': 'EOF', 'tipo': 'EOF', 'codigo': TOKEN_CODES['EOF']})
        return tokens_encontrados