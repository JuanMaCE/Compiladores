from .AST import *
from .analizador_sintactico import *
from .analizador_semantico import *
import subprocess
import os

codigo_fuente2 = """
float sumar(float a, float b) {
    return a + b;
}

void main() {
    float x;
    float y;
    printf("Ingrese Primer Numero: ")
    scanf("%f", &x);
    printf("Ingrese Segundo Numero: ")
    scanf("%f", &y);
    float resultado = sumar(x, y);
    printf("%f", &resultado);

    return 0;
}
"""

codigo_fuente3 = """
int sumar(int a, int b){
int suma = a + b;
return suma;
}

void main() {
int x = sumar(4, 5);
}
"""

def compile_and_run(asm_code, py_code):
    """Compila y ejecuta el código ensamblador"""
    '''try:
        with open("temp.asm", "w") as f:
            f.write(asm_code)

        subprocess.run(["nasm", "-f", "elf32", "temp.asm", "-o", "temp.o"])
        subprocess.run(["gcc", "-m32", "-no-pie", "temp.o", "-o", "temp"])
        subprocess.run(["./temp"])

        result = subprocess.run(["./temp"], capture_output=True, text=True)
        return result.stdout

    except subprocess.CalledProcessError as e:
        return f"Error de compilación: {e}"
    except Exception as e:
        return f"Error inesperado: {e}"'''
    
    with open("tempy.py", "w") as f:
        f.write(py_code)
    subprocess.run(["python3", "tempy.py"])


def analizar_c(codigo_c):
    tokens = identificar_tokens(codigo_c)
    arbol_ast = None
    try:
        print('\nIniciando analisis sintactico...')
        parser = Parser(tokens)
        arbol_ast = parser.parsear()
        print('Analisis sintactico completado sin errores')
    except SyntaxError as e:
        print(e)

    try:
        print('Iniciando analisis semantico...')
        analizador_semantico = AnalizadorSemantico()
        analizador_semantico.analizar(arbol_ast)
        print('Analisis semantico completado sin errores')
    except SyntaxError as e:
        print(e)

    try:
        parser = Parser(tokens)
        arbol_ast = parser.parsear()
        codigo_py = arbol_ast.traducir()
        print("------------------------------")
        print("Codigo Python")
        codigo_py = [linea.replace('\t', '    ') for linea in codigo_py]
        codigo_py.append("main()")
        codigo_completo = "\n".join(codigo_py)
        print(codigo_completo)
        print("------------------------------")
        print('')
        codigo_asm = arbol_ast.generar_codigo()
        print("------------------------------")
        print("Código Ensamblador Generado:")
        print(codigo_asm)
        compile_and_run(codigo_asm, codigo_completo)
        print("------------------------------")
    except SyntaxError as e:
        print(e)

#analizar_c(codigo_fuente3)