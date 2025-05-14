from logic.node import Node

class Grafodirigido():
    def __init__(self, cabeza: Node):
        self.head = cabeza
        self.adyacencia = {}
        self.adyacencia[self.head] = []
        self.code_c = "#include <stdio.h>" + "\n" + "int main() {" +" \n"

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
        if node.return_id() == 1:
            self.code_c += self.generate_entrada(node.informacion)

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

    def generate_entrada(self, var):
        txt = str(var)
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
