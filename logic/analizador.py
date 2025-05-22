from AST import *
from analizador_sintactico import *
from analizador_semantico import *

codigo_fuente = """
float sumar(float a, float b) {
    return a + b;
}

void main() {
    float x = 5.34;
    float y;
    printf("Ingrese Primer Numero: ")
    scanf("%f", &x);
    printf("Ingrese Segundo Numero: ")
    scanf("%f", &y);
    float resultado = sumar(x, y);

    if (resultado <= 0){
        printf("La suma %f + %f es: %f", &x, &y, &resultado);
    }

    while (resultado <= 5) {
        printf("%f", &resultado);
        break;
    }
    for (int i = 1; i <= 5; i++) {
        printf("%d", &i);
    }

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
        codigo_py = arbol_ast.traducir()
        print("------------------------------")
        print("Codigo Python")
        codigo_py = [linea.replace('\t', '    ') for linea in codigo_py]
        codigo_completo = "\n".join(codigo_py)
        print(codigo_completo)
        print("------------------------------")
        print('')
        '''codigo_asm = arbol_ast.generar_codigo()
        print("------------------------------")
        print("Código Ensamblador Generado:")
        print(codigo_asm)
        print("------------------------------")'''
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
