from .AST import *
from .tabla_simbolos import *

class AnalizadorSemantico:
    def __init__(self):
        self.tabla_simbolos= TablaSimbolos()

    def analizar(self, nodo):
        if isinstance(nodo, NodoAsignacion):
            yaesta = self.visitar_NodoAsignacion(nodo)
            if yaesta:
                print('si')
            else:
                tipo_expr = self.analizar(nodo.expresion)
                self.tabla_simbolos.declarar_variables(nodo.nombre[1], tipo_expr)
        elif isinstance(nodo, NodoDeclaracion):
            tipo = nodo.tipo
            nombre = nodo.nombre
            self.tabla_simbolos.declarar_variables(nombre, tipo)
        elif isinstance(nodo, NodoIdentificador):
            return self.tabla_simbolos.obtener_tipo_variable(nodo.nombre[1])
        elif isinstance(nodo, NodoNumero):
            tipo = self.visitar_NodoNumero(nodo)
            return tipo
        elif isinstance(nodo, NodoParametro):
            tipo = nodo.tipo
            nombre = nodo.nombre
            return self.tabla_simbolos.declarar_variables(nombre, tipo)
        elif isinstance(nodo, NodoOperacion):
            tipo_izq = self.analizar(nodo.izquierda)
            tipo_der = self.analizar(nodo.derecha)
            if tipo_izq != tipo_der:
                raise Exception(f"Error: Tipo incopatible en la operacion {tipo_izq} {nodo.operador} {tipo_der}")
            return tipo_izq
        elif isinstance(nodo, NodoFuncion):
            self.visitar_NodoFuncion(nodo)
        elif isinstance(nodo, NodoRetorno):
            self.visitar_NodoRetorno(nodo)
        elif isinstance(nodo, NodoLlamarFuncion):
            tipo_retorno, parametros = self.tabla_simbolos.obtener_info_funcion(nodo.nombre[1])
            if len(nodo.argumentos) != len(parametros):
                raise Exception(f"Error: la funcion {nodo.nombre} espera {len(parametros)} argumentos")
            for param in parametros:
                for arg in nodo.argumentos:
                    tipo = self.analizar(arg)
                    if param.tipo != tipo:
                        raise Exception(f'Error: se espera {param.tipo} se encontró {tipo}')
            return tipo_retorno
        elif isinstance(nodo, NodoPrograma):
            for funcion in nodo.funciones:
                self.analizar(funcion)
        
    def visitar_NodoFuncion(self, nodo):
        if nodo.nombre in self.tabla_simbolos.funciones:
            raise Exception(f'Error semántico: la función {nodo.nombre} ya está definida')
        
        self.tabla_simbolos.declarar_funcion(nodo.nombre, nodo.tipo[1], nodo.parametros)

        for param in nodo.parametros:
            self.analizar(param)

        for instruccion in nodo.cuerpo:
            self.analizar(instruccion)

    def visitar_NodoAsignacion(self, nodo):
        tipo_expresion = self.analizar(nodo.expresion)
        existe = self.tabla_simbolos.variables[nodo.nombre[1]] = {'tipo': tipo_expresion}
        if existe:
            return True
        else:
            return False

    def visitar_NodoOperacion(self, nodo):
        tipo_izquierda = self.analizar(nodo.izquierda)
        tipo_derecha = self.analizar(nodo.derecha)

        if tipo_izquierda != tipo_derecha:
            raise Exception('Error Semántico: Operación entre tipos incompatible')
        
        return tipo_izquierda
    
    def visitar_NodoNumero(self, nodo):
        return 'int' if '.' not in nodo.valor[1] else 'float'
    
    def visitar_NodoIdentificador(self, nodo):
        if nodo.nombre[1] not in self.tabla_simbolos:
            raise Exception(f'Error Semántico: La variable {nodo.nombre[1]} no ')
        
        return nodo.tipo
    
    def visitar_NodoRetorno(self, nodo):
        return self.analizar(nodo.expresion)