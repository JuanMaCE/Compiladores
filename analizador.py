from AST import *
from analizador_sintactico import *
from analizador_semantico import *

# === Ejemplo de Uso ===
codigo_fuente = """
int sumar(int a, int b) {
    return a + b;
}

int main() {
    int x = 5;
    int y = 7;
    int resultado = sumar(x, y);

    printf("La suma es: ", x, y, resultado);

    return 0;
}
"""

def main():
    tokens = identificar_tokens(codigo_fuente)
    print("Tokens encontrados:")
    for tipo, valor in tokens:
        print(f'{tipo}: {valor}')

    try:
        print('\nIniciando analisis sintactico...')
        parser = Parser(tokens)
        arbol_ast = parser.parsear()
        print('Analisis sintactico completado sin errores')
    except SyntaxError as e:
        print(e)

    try:
        parser = Parser(tokens)
        arbol_ast = parser.parsear()
        print('Arbol')
        codigo_asm = arbol_ast.generar_codigo() 
        print("Código Ensamblador Generado:")
        print(codigo_asm)
    except SyntaxError as e:
        print(e)

    try:
        analizador_semantico = AnalizadorSemantico()
        analisis = analizador_semantico.analizar(arbol_ast)
        print('Analizador Semantico Tabla Simbolos')

        for llave in (analizador_semantico.tabla_simbolos.keys()):
            valor = analizador_semantico.tabla_simbolos.get(llave)
            print(f'{llave}: {valor}')
    except SyntaxError as e:
        print(e)

main()
