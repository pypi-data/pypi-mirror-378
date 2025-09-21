import cmath

def quadratic(a, b, c):
    x1 = (-b + cmath.sqrt(b**2 - 4 * a * c)) / (2 * a)
    x2 = (-b - cmath.sqrt(b**2 - 4 * a * c)) / (2 * a)

    return x1, x2