from os.path import split

from logic.node import Node

class Grafodirigido():
    def __init__(self, cabeza: Node):
        self.head = cabeza
        self.adyacencia = {}
        self.adyacencia[self.head] = []
        self.code_c = "#include <stdio.h>" + "\n" + "int main() {" +" \n"
        self.variables = {}

    def agregar_vertice(self, id: int, tipo: int, informacion: str, shape) -> Node:
        new_node = Node(id, tipo, informacion, shape)
        if new_node not in self.adyacencia:
            self.adyacencia[new_node] = []
        return new_node  # Importante para usar luego en aristas

    def obtener_nodo_por_id(self, id: int) -> Node:
        for nodo in self.adyacencia:
            print(nodo.return_id(), id)
            if nodo.return_id() == id:
                return nodo
        return None  # Si no existe

    def agregar_arista(self, origen: int, destino: int):
        nodo_inicio = self.obtener_nodo_por_id(origen)
        nodo_final = self.obtener_nodo_por_id(destino)
        self.adyacencia[nodo_inicio].append(nodo_final)

    def caminos_grafo(self):
        inicio = self.head
        return self._caminos_grafo(inicio)

    def _caminos_grafo(self, node: Node) -> str:
        current = node.return_info()

        if len(self.adyacencia[node]) == 0:
            return current

        if len(self.adyacencia[node]) == 1:
            siguiente = self.adyacencia[node][0]
            return f"{current}({self._caminos_grafo(siguiente)})"

        if len(self.adyacencia[node]) == 2:
            izquierda = self.adyacencia[node][0]
            derecha = self.adyacencia[node][1]
            return f"{current}({self._caminos_grafo(izquierda)},{self._caminos_grafo(derecha)})"

        return current

    def generate_code_C(self):
        inicio = self.head
        return self._generate_code_C(inicio)

    def _generate_code_C(self, node: Node) -> str:
        current = node.return_info()

        if node.return_tipo() == 1:
            txt = node.informacion
            self.code_c += self.generate_entrada(txt) +"\n"
            self.variables[txt.split()[1]] = txt.split()[0]

        if node.return_tipo() == 2:
            new_text = self.generate_imprimir(node.informacion)
            self.code_c += new_text + "\n"
        elif node.return_tipo()  == 3:
            self.generate_lectura(node.informacion)

        elif node.return_tipo() == 5:
            self.code_c += "}"

        if len(self.adyacencia[node]) == 0:
            return current

        if len(self.adyacencia[node]) == 1:
            siguiente = self.adyacencia[node][0]

            return f"{current}({self._generate_code_C(siguiente)})"

        if len(self.adyacencia[node]) == 2:
            izquierda = self.adyacencia[node][0]
            derecha = self.adyacencia[node][1]
            return f"{current}({self._generate_code_C(izquierda)},{self._generate_code_C(derecha)})"

        return current

    def generate_imprimir(self, txt: str) -> str:
        words = txt.split()  # Dividir el texto en palabras
        var = words[1]

        if var in self.variables:
            type_var = self.variables[var]


        new_txt = ""
        if type_var == "int":
            new_txt = f'printf("%d\\n", {var});\n'
        elif type_var == "str" or type_var == "char[]":
            new_txt = f'printf("%s\\n", {var});\n'
        elif type_var == "bool":
            new_txt = f'printf("%d\\n", {var});\n'  # or use ?: for true/false text
        elif type_var == "float":
            new_txt = f'printf("%.2f\\n", {var});\n'
        elif type_var == "double":
            new_txt = f'printf("%.4lf\\n", {var});\n'
        elif type_var == "char":
            new_txt = f'printf("%c\\n", {var});\n'
        else:
            new_txt = f'printf("%s\\n", {var});\n'
        return new_txt

    def generate_lectura(self, texto):

        if len(texto.split()) == 2:
            self.code_c += f'scanf("%d", &{texto.split()[1]});' +"\n"
        else:
            self.code_c += texto + "\n"

    def generate_entrada(self, var):
        txt = str(var) + ";"
        return txt



    def mostrar(self):
        txt = ""
        for clave, lista_adyacente in self.adyacencia.items():
            txt += clave.return_info() + " -> "
            for adyacente in lista_adyacente:
                txt += adyacente.return_info() + " | "
            txt += "\n"
        return txt




    def eliminar(self, nodo: Node):
        if nodo in self.adyacencia:
            valor = self.adyacencia.pop(nodo)

        for clave, lista_adyacente in self.adyacencia.items():
            for adyacente in lista_adyacente:
                if adyacente == nodo:
                    lista_adyacente.remove(adyacente)


        return valor
