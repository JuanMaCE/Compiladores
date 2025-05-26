def sumar(a: int, b: int):
    suma = a + b
    print(f"{suma}\n")
    return suma

def main():
    x: int = 0
    x = int(input())
    y: int = 0
    y = int(input())
    a = sumar(x, y)

main()