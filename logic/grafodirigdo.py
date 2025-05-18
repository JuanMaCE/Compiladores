from os.path import split

from logic.node import Node

class Grafodirigido():
    def __init__(self, cabeza: Node):
        self.head = cabeza
        self.adyacencia = {}
        self.adyacencia[self.head] = []
        self.code_c = "#include <stdio.h>" + "\n" + "#include <stdbool.h> " "\n" +"int main() {" +" \n"
        self.variables = {}

    def agregar_vertice(self, id: int, tipo: int, informacion: str, shape) -> Node:
        new_node = Node(id, tipo, informacion, shape)
        if new_node not in self.adyacencia:
            self.adyacencia[new_node] = []
        return new_node  # Importante para usar luego en aristas

    def obtener_nodo_por_id(self, id: int) -> Node:
        for nodo in self.adyacencia:
            if nodo.return_id() == id:
                return nodo
        return None  # Si no existe

    def agregar_arista(self, origen: int, destino: int):
        nodo_inicio = self.obtener_nodo_por_id(origen)
        nodo_final = self.obtener_nodo_por_id(destino)
        self.adyacencia[nodo_inicio].append(nodo_final)

    def caminos_grafo(self):
        inicio = self.head
        nodos_visitados = []
        return self._caminos_grafo(inicio, nodos_visitados)

    def _caminos_grafo(self, node: Node, nodos_visitados) -> str:
        if node in nodos_visitados:
            print(node)
            return "CICLO"  # Para evitar ciclos
        nodos_visitados.append(node)
        current = node.return_info()
        hijos = self.adyacencia.get(node, [])

        if len(hijos) == 0:
            return current
        elif len(hijos) == 1:
            return f"{current}({self._caminos_grafo(hijos[0], nodos_visitados)})"
        elif len(hijos) == 2:
            izquierda = self._caminos_grafo(hijos[0], nodos_visitados)
            derecha = self._caminos_grafo(hijos[1], nodos_visitados)
            return f"{current}({izquierda},{derecha})"

    def generate_code_C(self):
        inicio = self.head
        nodos_visitados = []
        line = 1
        return self._generate_code_C(inicio, nodos_visitados, False, line)

    def _generate_code_C(self, node: Node, nodos_visitados, flag, line) -> str:
        current = node.return_info()
        if node in nodos_visitados:
            self.generate_while(node)
            self.flag2 = True
            return "CICLO"

        if node.return_tipo()  == 1:
            self.generate_lectura(node.informacion)

        elif node.return_tipo() == 2:
            new_text = self.generate_imprimir(node.informacion)
            self.code_c += new_text

        elif node.return_tipo() == 3:
            txt = node.informacion
            print(txt)

            self.code_c += self.generate_entrada(txt) + "\n"
            if len(txt.split()) > 1:
                self.variables[txt.split()[1]] = txt.split()[0]


        elif node.return_tipo() == 4:
            txt = self.generate_if(node.informacion)
            self.code_c += txt
            flag = True


        elif node.return_tipo() == 5:
                self.code_c += "}"

        if len(self.adyacencia[node]) == 0:
            return current


        nodos_visitados.append(node)
        current = node.return_info()
        hijos = self.adyacencia.get(node, [])

        if len(hijos) == 0:
            return current
        elif len(hijos) == 1:
            return self._generate_code_C(hijos[0], nodos_visitados, flag, line)
        elif len(hijos) == 2:

            if flag == False:
                izquierda = self._generate_code_C(hijos[0], nodos_visitados, flag, line)
                derecha = self._generate_code_C(hijos[1], nodos_visitados, flag, line)
            elif flag == True:
                izquierda = self._generate_code_C(hijos[0], nodos_visitados, flag, line)
                if izquierda == "CICLO":
                    derecha = self._generate_code_C(hijos[1], nodos_visitados, flag, line)
                else:
                    self.code_c += "\n" + "else{" + "\n"
                    derecha = self._generate_code_C(hijos[1], nodos_visitados, flag, line)
                    self.code_c += "}"
                flag = False



        return current

    def generate_while(self, node):
        search_txt = self.generate_if(node.informacion) + "\n"
        lines_of_code = self.code_c.splitlines()
        characters = self.code_c.split()
        txt_with_while = ""
        for i in range(len(lines_of_code)):
            if lines_of_code[i].strip() == search_txt.strip():
                lines_of_code[i] = f"while ({node.informacion}) ""{"
            txt_with_while += lines_of_code[i] + "\n"
        txt_with_while += "}" + "\n"
        self.code_c = txt_with_while


    def generate_imprimir(self, txt: str) -> str:
        words = txt.split()
        if len(words) == 2:# Dividir el texto en palabras
            var = words[1]
            new_txt = ""
            print(self.variables)

            if var in self.variables:
                type_var = self.variables[var]

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
        else:
            return txt

    def generate_if(self, condicion: str):
        new_txt = f"if ({condicion}) ""{" + "\n"
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
