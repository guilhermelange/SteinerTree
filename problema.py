import sys
import graphviz
from pyomo.environ import *
from itertools import chain, combinations
from time import time

M = 100000

def gera_matriz_arestas(qtd_vertices, valor_default):
    m = [[] for _ in range(qtd_vertices)]
    for i in range(qtd_vertices):
        m[i] = [valor_default for _ in range(qtd_vertices)]
    return m

def gera_pdf(nome, arestas, modelo, steiner):
    lastidx = -1
    print(nome)
    for i, c in enumerate(nome):
        if c in ['/', '\\']:
            lastidx = i
    nome = nome[lastidx+1:]
    print(nome)

    verts = len(arestas)
    g = graphviz.Graph(nome, engine='neato')
    g.attr('edge', {'fontsize': '8'})
    for a in range(verts):
        if a in steiner:
            g.attr('node', {'shape': 'circle', 'color': 'aqua', 'width': '0.05'})
        else:
            g.attr('node', {'shape': 'circle', 'color': 'crimson', 'width': '0.05'})
        g.node(str(a), label=str(a))
        
    for b in range(verts):
        for a in range(b):
            if arestas[a][b] == M:
                continue
            attr = {'weight': str( int(1000 - 1000*arestas[a][b]) )}
            if modelo is not None and modelo[a][b]:
                if arestas[a][b] > 0:
                    attr['color'] = 'red'
                    attr['penwidth'] = '3'
            label = str(arestas[a][b])
            g.edge(str(a), str(b), label, attr)

    dir = 'output'
    print(f'Grafo gerado: {nome}, disponível em {g.render(directory=dir)}')


def leitura_instancia(file):
    linhas = file.readlines()
    linhas = map(lambda l: l[:-1], linhas)  # remove quebras de linha
    
    vertices_terminais = int(next(linhas))
    vertices_steiner = int(next(linhas))
    vertices = vertices_terminais + vertices_steiner
    pesos = gera_matriz_arestas(vertices, M)

    terminais = []
    steiner = []

    for linha in linhas:
        dados = linha.split(' ')
        if dados[0] == 'T':
            terminais.append(int(dados[1])-1)
        else:
            a, b, w = int(dados[1]), int(dados[2]), float(dados[3])
            a -= 1
            b -= 1
            pesos[a][b] = w
            pesos[b][a] = w

    for i in range(0, vertices):
        if i not in terminais:
            steiner.append(i)

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

print('Executando leitura de instâncias...')
file = open(sys.argv[1], 'r')
timelimit = sys.argv[2]
arestas, terminais, steiner = leitura_instancia(file)

vertices = terminais + steiner
subconjuntos = gera_subconjuntos(vertices, terminais, arestas)
size = len(vertices)

print('Executando algoritmo de programação inteira linear...')
resultado = executa_arvore_steiner(vertices, arestas, subconjuntos, timelimit)

print('')
print('Terminais: ', terminais)
print('Steiner: ', steiner)
print('Arestas: ', resultado['arestas'])
print('Peso das arestas', resultado['peso'])
print('Tempo: ', resultado['tempo'])
print('')

if '--visual' in sys.argv:
    print('Gerando PDF...')
    gera_pdf(sys.argv[1], arestas, resultado['modelo'], steiner)