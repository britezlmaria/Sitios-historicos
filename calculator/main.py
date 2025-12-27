from src import calculator

if __name__ == "__main__":
    num: float = float(input("Ingresa un numero: "))
    otro_num: float = float(input("Ingresa otro numero: "))
    operacion: str = input("Ingresa una operacion (+, -, *, /): ")
    result: float = calculator.calculate(num, otro_num, operacion)
    print(result)
