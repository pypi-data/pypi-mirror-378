# -*- coding: utf-8 -*-
"""grammar"""

from simple_calculator_muharram_nizar.parser import Parser


class Analyzer(object):

    def __init__(self, initial_entry):
        self.preanalysis = ''
        self.parser = Parser(initial_entry)

    def next_token(self):
        """Gets the next token and calculates preanalysis."""

        token = self.parser.next_token()
        if token is None:
            self.preanalysis = '$'
        else:
            self.preanalysis = token

    def analyze(self):
        self.next_token()
        result = self.start()

        if self.preanalysis != '$':
            raise Exception('Found ' + self.preanalysis + ', expecting ' + "'$'")

        return result

    def start(self):
        return self.e()

    def e(self):
        """E -> T E'"""

        t = self.t()
        e_prime = self.e_prime()

        if e_prime is None:
            return t
        else:
            if e_prime[0] == '+':
                return t + e_prime[1]
            elif e_prime[0] == '-':
                return t - e_prime[1]

    def e_prime(self):
        """E' -> + T E' | - T E' | epsilon"""

        if self.preanalysis == '+' or self.preanalysis == '-':
            op = self.preanalysis
            self.next_token()
            t = self.t()
            e_prime = self.e_prime()

            if e_prime is None:
                return (op, t)
            else:
                if e_prime[0] == '+':
                    return (op, t + e_prime[1])
                elif e_prime[0] == '-':
                    return (op, t - e_prime[1])
        else:
            return None

    def t(self):
        """T -> F T'"""

        f = self.f()
        t_prime = self.t_prime()

        if t_prime is None:
            return f
        else:
            if t_prime[0] == '*':
                return f * t_prime[1]
            elif t_prime[0] == '/':
                return f / t_prime[1]

    def t_prime(self):
        """T' -> * F T' | / F T' | epsilon"""

        if self.preanalysis == '*' or self.preanalysis == '/':
            op = self.preanalysis
            self.next_token()
            f = self.f()
            t_prime = self.t_prime()

            if t_prime is None:
                return (op, f)
            else:
                if t_prime[0] == '*':
                    return (op, f * t_prime[1])
                elif t_prime[0] == '/':
                    return (op, f / t_prime[1])
        else:
            return None

    def f(self):
        """F -> P F'"""

        p = self.p()
        f_prime = self.f_prime()

        if f_prime is None:
            return p
        else:
            if f_prime[0] == '^':
                return p ** f_prime[1]

    def f_prime(self):
        """F' -> ^ P F' | epsilon"""

        if self.preanalysis == '^':
            op = self.preanalysis
            self.next_token()
            p = self.p()
            f_prime = self.f_prime()

            if f_prime is None:
                return (op, p)
            else:
                if f_prime[0] == '^':
                    return (op, p ** f_prime[1])
        else:
            return None

    def p(self):
        """P -> N | ( E )"""

        if self.preanalysis == '(':
            self.next_token()
            e = self.e()
            if self.preanalysis == ')':
                self.next_token()
                return e
            else:
                raise Exception('Found ' + self.preanalysis + ', expecting ' + "')'")
        else:
            return self.n()

    def n(self):
        """N -> integer | decimal"""

        number = self.preanalysis
        self.next_token()
        try:
            return int(number)
        except ValueError:
            return float(number)


