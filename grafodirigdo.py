from node import Node

class Grafodirigido():
    def __init__(self):
        self.adyacencia = {}

    def agregar_vertice(self, tipo: int, informacion: str) -> Node:
        new_node = Node(tipo, informacion)
        if new_node not in self.adyacencia:
            self.adyacencia[new_node] = []
        return new_node  # Importante para usar luego en aristas

    def obtener_nodo_por_info(self, informacion: str) -> Node:
        for nodo in self.adyacencia:
            if nodo.informacion == informacion:
                return nodo
        return None  # Si no existe

    def agregar_arista(self, origen: Node, destino: Node):
        if origen in self.adyacencia and destino in self.adyacencia:
            self.adyacencia[origen].append(destino)
        else:
            raise ValueError("Uno o ambos nodos no existen en el grafo")



    def mostrar(self):
        txt = ""
        for vertice, arista in self.adyacencia.items(): # esto muestra las aristas
            txt += str(vertice)+ "->" + str(arista) + "\n"
        return  txt

