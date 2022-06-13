from arvore_steiner import *
import sys

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
print('Arestas: ', resultado['arestas'])
print('Peso das arestas', resultado['peso'])
print('Tempo: ', resultado['tempo'])
print('')

if '--visual' in sys.argv:
    print('Gerando PDF...')
    gera_pdf(sys.argv[1], arestas, resultado['modelo'], steiner)