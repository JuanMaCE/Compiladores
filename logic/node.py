
class Node:
    # TIPO
    # 0  = INICIO de programa
    # 1 = Entrada de datos
    # 2 = Salida de datos
    # 3 = Proceso
    # 4 = Condición
    # 5 = Final
    # 6 = llamar funcion

    def __init__(self, id: int, tipo: int, informacion: str, shape):
        self.id = id
        self.tipo = tipo
        self.informacion = informacion
        self.shape = shape
        self.id_graph = None



    def return_tipo(self):
        return self.tipo

    def return_info(self):
        return str(self.id)

    def return_id(self):
        return self.id

    def node_change_info(self, txt):
        self.informacion = txt

    def connect_graph(self, id_graph: int):
        self.id_graph = id_graph
        return self.id_graph