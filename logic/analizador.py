from AST import *
from analizador_sintactico import *
from analizador_semantico import *

codigo_fuente = """
int sumar(int a, int b) {
    return a + b;
}

void main() {
    int x;
    int y;
    printf("Ingrese Primer Numero: ")
    scanf("%d", &x);
    printf("Ingrese Segundo Numero: ")
    scanf("%d", &y);
    int resultado = sumar(x, y);
    printf("%d", &resultado);

    return 0;
}
"""

def guardar_codigo_asm(nombre_archivo: str, codigo: str):
    with open(nombre_archivo+'.asm', "w") as archivo:
        archivo.write(codigo)

def main():
    tokens = identificar_tokens(codigo_fuente)
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
        codigo_py = arbol_ast.traducir()
        print("------------------------------")
        print("Codigo Python")
        codigo_py = [linea.replace('\t', '    ') for linea in codigo_py]
        codigo_completo = "\n".join(codigo_py)
        print(codigo_completo)
        print("------------------------------")
        print('')
        codigo_asm = arbol_ast.generar_codigo()
        print("------------------------------")
        print("Código Ensamblador Generado:")
        print(codigo_asm)
        guardar_codigo_asm('nombrearchivo', codigo_asm)
        print("------------------------------")
    except SyntaxError as e:
        print(e)

    try:
        print('Iniciando analisis semantico...')
        analizador_semantico = AnalizadorSemantico()
        analizador_semantico.analizar(arbol_ast)
        print('Analisis semantico completado sin errores')
    except SyntaxError as e:
        print(e)

main()
