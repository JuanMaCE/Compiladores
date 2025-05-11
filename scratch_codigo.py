from grafodirigdo import Grafodirigido


def agregar_datos(grafo: Grafodirigido):
    grafo.agregar_vertice("inicio")
    grafo.agregar_vertice("i = 1")
    grafo.agregar_vertice("i == 2")
    grafo.agregar_vertice("si")
    grafo.agregar_vertice("no")
    grafo.agregar_vertice("fin")
    grafo.agregar_vertice("error")

    grafo.agregar_arista("inicio","i = 1")
    grafo.agregar_arista("i = 1", "i == 2")
    grafo.agregar_arista("i == 2","si")
    grafo.agregar_arista("i == 2","no" )
    grafo.agregar_arista("si","fin")
    grafo.agregar_arista("no", "error")



def main():
    grafo = Grafodirigido()
    agregar_datos(grafo)

    print(grafo.mostrar())
    print("hola")

main()