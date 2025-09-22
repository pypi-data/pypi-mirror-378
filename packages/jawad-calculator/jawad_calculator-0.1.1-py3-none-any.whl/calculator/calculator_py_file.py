class Calculator:
    def addition(self, a, b):
        return a + b

    def subtraction(self, a, b):
        return a - b

# Example usage
if __name__ == "__main__":
    calc = Calculator()
    print("Addition:", calc.addition(10, 5))
    print("Subtraction:", calc.subtraction(10, 5))