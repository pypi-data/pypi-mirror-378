def discriminant(a, b, c):
    d = b**2 - 4*a*c

    if d > 0:
        return "Roots are real and not equal"
    elif d == 0:
        return "Roots are real and equal"
    else:
        return "Roots are not real"