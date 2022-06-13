import graphviz
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