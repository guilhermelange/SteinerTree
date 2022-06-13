import sys
from utils import gera_matriz_arestas, gera_pdf, M
from pyomo.environ import *
from itertools import chain, combinations
from time import time

def leitura_instancia(file):
    linhas = file.readlines()
    linhas = map(lambda l: l[:-1], linhas)  # remove quebras de linha
    
    vertices_terminais = int(next(linhas))
    vertices_steiner = int(next(linhas))
    vertices = vertices_terminais + vertices_steiner
    pesos = gera_matriz_arestas(vertices, M)

    terminais = []
    for i in range(0, vertices_terminais):
        terminais.append(i)

    steiner = []
    for i in range(vertices_terminais, vertices_terminais + vertices_steiner):
        steiner.append(i)

    for linha in linhas:
        dados = linha.split(' ')
        a, b, w = int(dados[0]), int(dados[1]), float(dados[2])
        pesos[a][b] = w
        pesos[b][a] = w

    return pesos, terminais, steiner

def gera_subconjuntos(vertices, terminais, arestas):
    def gera_combinacoes(lista_in):
        lista = list(lista_in)
        return chain.from_iterable(combinations(lista, r) for r in range(len(lista)+1))

    def possui_terminal(lista01, lista02):
        for i in lista01:
            if i in lista02:
                return True
        return False

    def valida_arestas(conjunto):
        if len(conjunto) <= 0:
            return False
        elif len(conjunto) == 1:
            return True
        else:
            for i in conjunto:
                valido = False
                for j in conjunto:
                    if i != j and arestas[i][j] != M: # 100000
                        valido = True
                        break

                if valido == False:
                    return False
            return True
        
    def valida_subconjunto_terminal(conjunto):
        return len(set(terminais).intersection(conjunto)) != len(terminais)

    v = len(vertices)
    subconjuntos = []
    for x in gera_combinacoes(vertices):
        if len(x) > 0 and len(x) <= v-1:
            if possui_terminal(x, terminais):
                temp = list(x)
                if valida_arestas(temp):
                    if valida_subconjunto_terminal(temp):
                        subconjuntos.append(temp)
    return subconjuntos

def executa_arvore_steiner(vertices, arestas, subconjuntos, timelimit):
    v = len(arestas)
    size = len(vertices)
    model = ConcreteModel()
    # Variáveis de Decisão
    model.x = Var(range(v), range(v), domain=Boolean) # Aresta Selecionada?

    # Função Objetivo
    model.obj = Objective( \
        sense=minimize, \
        expr=sum(arestas[i][j] * model.x[i,j] for i in range(v) for j in range(i, v)) \
    )

    # Restrições
    model.con = ConstraintList()
    
    # Restrição 01: Remover situações em que a aresta foi selecionada em ambas as direções. [i][j] and [j][i]
    vs = list(range(v))
    combinacoes = chain.from_iterable(combinations(vs, r) for r in range(1, len(vs)))
    for c in combinacoes:
        model.con.add(expr=sum(model.x[i,j] for i in c for j in c if i <= j) <= len(c) - 1)

    # Restrição 02: Para cada Subconjunto gerado, verifica se há uma aresta atravessando sua fronteira
    for sub in subconjuntos:
        sub_auxiliar = []
        for i in sub:
            for j in range(0, size):
                if j not in sub:
                    if i <= j:
                        index1 = i
                        index2 = j
                    else:
                        index1 = j
                        index2 = i
                    sub_auxiliar.append([index1, index2])
        if len(sub_auxiliar) > 0:
            model.con.add(sum(model.x[item[0], item[1]] for item in sub_auxiliar) >= 1)
    
    time_inicio = time()
    solver = SolverFactory('glpk')
    solver.solve(model, timelimit)
    time_fim = time()

    arestas_selecionadas = []
    modelo = gera_matriz_arestas(v, False)
    for i in range(v):
        for j in range(i, v):
            if model.x[i,j]() == 1:
                arestas_selecionadas.append((arestas[i][j], i, j))
                modelo[i][j] = True
                modelo[j][i] = True
    peso = model.obj()

    return { \
        'modelo': modelo, \
        'arestas': arestas_selecionadas, \
        'peso': peso, \
        'tempo': time_fim - time_inicio \
    }