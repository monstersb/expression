#! /usr/bin/env ipython
#! -*- coding: utf-8 -*-

from pprint import pprint

blank = " \t\r\n"
operator = ['!=<>&|', ['==', '!=', '>', '>=', '<', '<=', '!', '||', '&&']]

class SyntaxError(Exception):
    pass

def if_else(condition, a, b):
    if condition:
        return a
    else:
        return b

class Render(object):
    def __init__(self, pattern):
        self.__pattern = filter(lambda x : x not in blank, '(%s)' % pattern)
        return self.__compile()

    def __compile(self):
        self.__tokenize()
        self.__parse()
        self.__check(self.__expression)

    def __tokenize(self):
        self.__token = []
        t = None
        for i in self.__pattern:
            while True:
                if not t:
                    if i.isalpha() or i == '_':
                        t = [0, i]
                    elif i.isdigit():
                        t = [1, [int(i)]]
                    elif i in operator[0]:
                        t = [2, i]
                    elif i == '(' or i == ')':
                        t = [3, i]
                    else:
                        raise SyntaxError('invalid token : ' + i)
                else:
                    if t[0] == 0:
                        if i.isalnum() or i == '_':
                            t[1] += i
                        else:
                            self.__token.append((t[0], t[1]))
                            t = None
                            continue
                    elif t[0] == 1:
                        if i.isdigit():
                            t[1][-1] = t[1][-1] * 10 + int(i)
                        elif i == '.':
                            t[1].append(0)
                        else:
                            self.__token.append((t[0], t[1]))
                            t = None
                            continue
                    elif t[0] == 2:
                        if t[1] == '!':
                            self.__token.append((t[0], t[1]))
                            t = None
                            continue
                        if i in operator[0] and i is not '!':
                            t[1] += i
                        else:
                            if t[1] in operator[1]:
                                self.__token.append((t[0], t[1]))
                                t = None
                                continue
                            else:
                                raise SyntaxError('invalid operator : ' + t[1])
                    elif t[0] == 3:
                        self.__token.append((t[0], t[1]))
                        t = None
                        continue
                break
        self.__token.append((t[0], t[1]))

    def __parse(self):
        self.__expression = []
        stack = []
        for i in self.__token:
            if i[0] == 3 and i[1] == '(':
                stack.append(self.__expression)
                self.__expression.append([])
                self.__expression = self.__expression[-1]
            elif i[0] == 3 and i[1] == ')':
                if len(stack) == 0:
                    raise SyntaxError('Unexpected ")"')
                tor = [(2, '||')]
                for i in self.__splitlist(self.__expression, (2, '||')):
                    tand = [(2, '&&')]
                    for j in self.__splitlist(i, (2, '&&')):
                        exp = []
                        tnot = []
                        for k in j:
                            if k == (2, '!'):
                                tnot.append('not')
                            elif tnot:
                                n = len(tnot)
                                tnot = k
                                for i in range(n):
                                    tnot = [(2, '!'), tnot]
                                exp.append(tnot)
                                tnot = []
                            else:
                                exp.append(k)
                        tand.append(exp)
                    tor = tor + [tand]
                self.__expression[:] = [tor]
                self.__expression = stack.pop()
            else:
                self.__expression.append(i)
        if stack:
            raise SyntaxError('Unexpected ")"')
        self.__expression = self.__expression[0]
    
    def __splitlist(self, mlist, sp):
        result = [[]]
        n = 0
        for i in mlist:
            if i == sp:
                result.append([])
                n += 1
            else:
                result[n].append(i)
        return result
    
    def __check(self, exp):
        for i in exp:
            if type(i) is list:
                self.__check(i)
        if not (len(exp) == 1 and type(exp[0]) is list)\
                and not (len(exp) == 2 and exp[0] == (2, '!') and type(exp[1]) is list)\
                and not (len(exp) == 3 and exp[0][0] == 0 and exp[1][0] == 2 and exp[2][0] == 0)\
                and not (len(exp) == 3 and exp[0][0] == 0 and exp[1][0] == 2 and exp[2][0] == 1)\
                and not (len(exp) == 3 and exp[0][0] == 0 and exp[1][0] == 2 and type(exp[2]) is list)\
                and not (len(exp) == 3 and exp[0][0] == 1 and exp[1][0] == 2 and exp[2][0] == 0)\
                and not (len(exp) == 3 and exp[0][0] == 1 and exp[1][0] == 2 and exp[2][0] == 1)\
                and not (len(exp) == 3 and exp[0][0] == 1 and exp[1][0] == 2 and type(exp[2]) is list)\
                and not (len(exp) == 3 and type(exp[0]) is list and exp[1][0] == 2 and exp[2][0] == 0)\
                and not (len(exp) == 3 and type(exp[0]) is list and exp[1][0] == 2 and exp[2][0] == 1)\
                and not (len(exp) == 3 and type(exp[0]) is list and exp[1][0] == 2 and type(exp[2]) is list)\
                and not (exp[0] == (2, '||'))\
                and not (exp[0] == (2, '&&')):
            raise SyntaxError()
    
    def __calc(self, exp, v):
        if len(exp) == 1:
            return self.__calc(exp[0], v)
        elif len(exp) == 2 and exp[0] == (2, '!'):
            return not self.__calc(exp[1], v)
        elif len(exp) == 3 and exp[1][0] == 2:
            if exp[0][0] == 0:
                r1 = v[exp[0][1]]
            elif exp[0][0] == 1:
                r1 = exp[0][1]
            elif type(exp[0]) is list:
                r1 = self.__calc(exp[0], v)
            if exp[2][0] == 0:
                r2 = v[exp[2][1]]
            elif exp[2][0] == 1:
                r2 = exp[2][1]
            elif type(exp[2]) is list:
                r2 = self.__calc(exp[2], v)
            return eval('%s%s%s' % (r1, exp[1][1], r2))
        else:
            r = map(lambda x : self.__calc(x, v), exp[1:])
            if exp[0] == (2, '||'):
                return reduce(lambda a, b : a or b, r, False)
            elif exp[0] == (2, '&&'):
                return reduce(lambda a, b : a and b, r, True)
        
    def calculate(self, value):
        v = {i:[int(j) for j in value[i].split('.')] for i in value}
        return self.__calc(self.__expression, v)


if __name__ == '__main__':
    pattern = 'a > 1.0.1 && (b > c || c <= 5.0.9) && !(a == b)'
    test = {'a':'0.0.2', 'b':'3.2.1', 'c':'3.2.1'}
    print 'pattern : ', pattern
    print 'test    : ', test
    print Render(pattern).calculate(test)
