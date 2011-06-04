""" Utility for generating random code snippets of the form:

     a = foo(b)
     c,z = bar(d,e)
     ...

    It is used for testing in a variety of places.
"""
import doctest
import random


def random_code_generator(lines=100):
    """ Generate multiple lines of function call code.

        Each function has a random name and a random number of inputs and
        outputs varying from 1 to 5.

        Example:
            >>> import random
            >>> random.seed(1000)
            >>> print random_code_generator(5)
            z, d, r = mfrflbzmms(r, c, j, m)
            x, y, z = sceciaw(x, a, x)
            h = rgqxwhlmhi(u, o)
            x, j, f, w = nijhtmfwtwygxtk(a, d, q, b, h)
            m = mkxzybwfiwcdgfisqety(o, p)
    """
    alphabet = "abcdefghijklmnopqrstuxwxyz"
    functions = []
    for i in range(lines):
        input_count = random.randint(1,5)
        inputs = [random.choice(alphabet) for i in range(input_count)]
        output_count = random.randint(1,5)
        outputs = [random.choice(alphabet) for i in range(output_count)]

        name_len = random.randint(5,20)
        name = ''.join([random.choice(alphabet) for i in range(name_len)])
        functions.append("%s = %s(%s)" % (', '.join(outputs),
                                         name,
                                         ', '.join(inputs)))

    return '\n'.join(functions)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
