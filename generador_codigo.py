# ==========================================
# Archivo: generador_codigo.py
# ==========================================
class GeneradorCodigoIntermedio:
    def __init__(self, tabla_simbolos):
        self.tabla = tabla_simbolos

    def generar(self):
        codigo = []
        codigo.append("; --- GENERACIÓN DE DIRECTIVAS TS ---")
        codigo.append(".DATA\n")
        
        for nombre, info in self.tabla.items():
            linea = f"{nombre}\t{info['directiva']}\t?\t\t; Memoria: {info['direccion']}"
            codigo.append(linea)
            
        return "\n".join(codigo) 

    