# Requirido:
- Python
- GLPK
- graphviz
    - Instalação local e definição no PATH: https://graphviz.org/download/
    - Instalação lib: pip install graphviz

# UDESC - 55MQU
- Modelo matemático linear desenvolvido conforme: https://homepage.univie.ac.at/ivana.ljubic/research/publications/NetworksSI.pdf (Página 9)
- Instâncias disponíveis no diretório /instances
- Os relatório gerados conforme adição do parâmetro --visual ficam disponíveis no diretório /output
- Parâmetros de Entrada:
    1 - Nome da Instância.
    2 - Timeout
    3 - --visual
    Ex: main.py instances/exemplo03.txt --visual