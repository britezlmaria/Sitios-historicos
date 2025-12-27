from src import operations

def calculate(a: float, b: float, operation: str) -> int:
    if operation == "+":
        return operations.add(a, b)
    elif operation == "-":
        return operations.substract(a, b)
    elif operation == "/":
        return operations.div(a, b)
    elif operation == "*":
        return operations.mult(a, b)
    else:
        return "Invalid operation"
