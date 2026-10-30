from calculator import add, divide, multiply, subtract


def main():
    a, b ,c = 10, 2, 308
    print(f"{a} + {b} = {add(a, b)}")
    print(f"{a} - {b} = {subtract(a, b)}")
    print(f"{a} * {b} = {multiply(a, b)}")
    print(f"{a} / {b} = {divide(a, b)}")


if __name__ == "__main__":
    main()
