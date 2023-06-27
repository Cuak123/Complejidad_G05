import graphviz as gv
import csv
import difflib
import json

from flask import Flask, request, jsonify
from flask_cors import CORS
# Flask app


class Receta:
    def __init__(self, padre, id, nombre, tiempo, categoria, hijos, ingredientes):
        self.nombre = nombre
        self.tiempo = tiempo
        self.categoria = categoria
        self.id = id
        self.padre = padre
        self.hijos = hijos
        self.ingredientes = ingredientes

def inicializar():
    lista_recetas = []
    cont_id = 5
    nodo_vacio = Receta(0, 0, "", "", "", [], [])
    lista_recetas.append(nodo_vacio)
    nodo_vacio = Receta(1, 1, "", "", "Recetas de Aperitivos y tapas", [], [])
    lista_recetas.append(nodo_vacio)
    nodo_vacio = Receta(2, 2, "", "", "Recetas de Arroces y cereales", [], [])
    lista_recetas.append(nodo_vacio)
    nodo_vacio = Receta(3, 3, "", "", "Recetas de Aves y caza", [], [])
    lista_recetas.append(nodo_vacio)
    nodo_vacio = Receta(4, 4, "", "", "Recetas de Carne", [], [])
    lista_recetas.append(nodo_vacio)
    nodo_vacio = Receta(5, 5, "", "", "Recetas de Ensaladas", [], [])
    lista_recetas.append(nodo_vacio)
    with open('dataset_recetas.csv', 'r') as archivo_csv:
        lector_csv = csv.reader(archivo_csv, delimiter=';')
        for fila in lector_csv:
            cont_id += 1
            id = cont_id
            padre = cont_id
            hijos = []
            nombre = fila[2]
            tiempo = fila[3]
            categoria = fila[1]
            ingredientes_celda = fila[5]
            ingredientes = ingredientes_celda.split(',')
            ingredientes = [ingrediente.strip() for ingrediente in ingredientes]
            nueva_receta = Receta(padre, id, nombre, tiempo, categoria, hijos, ingredientes)
            lista_recetas.append(nueva_receta)
    archivo_csv.close()
    return lista_recetas

def find(s, a):
    i = a
    while s[i].padre != i:
        i = s[i].padre
    return i

def union(s, a, b):
    pa = find(s, a)
    pb = find(s, b)
    s[pa].padre = pb

def drawDS(ds):
    graph = gv.Digraph("DisjointSet")
    graph.graph_attr['rankdir'] = "BT"
    for e, p in enumerate(ds):
        graph.node(str(e))
        if p.padre != e:
            graph.edge(str(e), str(p.padre))
    return graph

def verificar_palabra_comun(lista1, lista2):
    for ingrediente1 in lista1:
        palabras1 = ingrediente1.split()
        for ingrediente2 in lista2:
            palabras2 = ingrediente2.split()
            for palabra1 in palabras1:
                for palabra2 in palabras2:
                    if palabra1.lower() == palabra2.lower():
                        return True
    return False

def bfs_al_eliminar_ingrediente(G, s, lista_ingredientes_eliminar):
    n = len(G)
    visited = [False] * n
    queue = [s]
    visited[s] = True

    while queue:
        u = queue.pop(0)
        for v in G[u].hijos:
            if not visited[v]:
                visited[v] = True
                queue.append(v)
            if v not in [1, 2, 3, 4, 5]:
                if verificar_palabra_comun(lista_ingredientes_eliminar, G[v].ingredientes):
                    G[v].padre = v
                    G[u].hijos.remove(v)

def bfs_al_categoria_filtro(G, s, list_categoria):
    n = len(G)
    visited = [False] * n
    queue = [s]
    visited[s] = True

    while queue:
        u = queue.pop(0)
        for v in G[u].hijos:
            if not visited[v]:
                visited[v] = True
                if G[v].categoria in list_categoria:
                    queue.append(v)
                else:
                    G[v].padre = v
                    G[u].hijos.remove(v)

def Buscar_receta_tiempo(tiempo_buscado, lista_recetas):
    nodos_aperitivos = []
    nodos_arroces = []
    nodos_aves = []
    nodos_carne = []
    nodos_ensaladas = []

    for receta in lista_recetas:
        if receta.tiempo == tiempo_buscado:
            if receta.categoria == "Recetas de Aperitivos y tapas":
                nodos_aperitivos.append(receta.id)
        if receta.categoria == "Recetas de Arroces y cereales":
            nodos_arroces.append(receta.id)
        if receta.categoria == "Recetas de Aves y caza":
            nodos_aves.append(receta.id)
        if receta.categoria == "Recetas de Carne":
            nodos_carne.append(receta.id)
        if receta.categoria == "Recetas de Ensaladas":
            nodos_ensaladas.append(receta.id)

    for i in range(len(nodos_aperitivos)):
        b = nodos_aperitivos[i]
        union(lista_recetas, b, lista_recetas[1].padre)
        lista_recetas[1].hijos.append(b)

    arroces_1 = nodos_arroces[0]
    for i in range(1, len(nodos_arroces)):
        b = nodos_arroces[i]
        union(lista_recetas, b, lista_recetas[2].padre)
        lista_recetas[2].hijos.append(b)

    aves_1 = nodos_aves[0]
    for i in range(1, len(nodos_aves)):
        b = nodos_aves[i]
        union(lista_recetas, b, lista_recetas[3].padre)
        lista_recetas[3].hijos.append(b)

    carne_1 = nodos_carne[0]
    for i in range(1, len(nodos_carne)):
        b = nodos_carne[i]
        union(lista_recetas, b, lista_recetas[4].padre)
        lista_recetas[4].hijos.append(b)

    ensalada_1 = nodos_ensaladas[0]
    for i in range(1, len(nodos_ensaladas)):
        b = nodos_ensaladas[i]
        union(lista_recetas, b, lista_recetas[5].padre)
        lista_recetas[5].hijos.append(b)

    union(lista_recetas, lista_recetas[1].padre, 0)
    union(lista_recetas, lista_recetas[2].padre, 0)
    union(lista_recetas, lista_recetas[3].padre, 0)
    union(lista_recetas, lista_recetas[4].padre, 0)
    union(lista_recetas, lista_recetas[5].padre, 0)

    lista_recetas[0].hijos.append(lista_recetas[1].id)
    lista_recetas[0].hijos.append(lista_recetas[2].id)
    lista_recetas[0].hijos.append(lista_recetas[3].id)
    lista_recetas[0].hijos.append(lista_recetas[4].id)
    lista_recetas[0].hijos.append(lista_recetas[5].id)

def bfs_Get_lista(G, s):
    n = len(G)
    visited = [False]*n
    queue = [s]
    nueva_ListaRecetas = []
    visited[s] = True
    nueva_ListaRecetas.append(G[s])
    while queue:
        u = queue.pop(0)
        for v in G[u].hijos:
            if not visited[v]:
                visited[v] = True
                nueva_ListaRecetas.append(G[v])
                queue.append(v)
                print(str(G[v].id) + " - "+ G[v].nombre)
    return nueva_ListaRecetas

import json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def convert_json(lista_recetas):
    lista_diccionarios = []
    for receta in lista_recetas:
        diccionario_receta = {
            "padre": receta.padre,
            "id": receta.id,
            "nombre": receta.nombre,
            "tiempo": receta.tiempo,
            "categoria": receta.categoria,
            "hijos": receta.hijos,
            "ingredientes": receta.ingredientes
        }
        lista_diccionarios.append(diccionario_receta)
    json_recetas = json.dumps(lista_diccionarios)
    return json_recetas

@app.route('/api/procesar_valores', methods=['POST', 'GET'])
def procesar_valores():
    if request.method == 'GET':
        tiempo = request.args.get('tiempo')
        tipo = request.args.get('tipo')
        alimento = request.args.get('alimento')
        return funcion_principal(tiempo, tipo, alimento)
    else:
        datos = request.get_json()
        if 'datos' in datos:
            tiempo = datos.get('tiempo')
            tipo = datos.get('tipo')
            alimento = datos.get('alimento')
        return funcion_principal(tiempo, tipo, alimento)

def funcion_principal(tiempo, tipo, alimento):
    lista_recetas = inicializar()
    Buscar_receta_tiempo(tiempo, lista_recetas)
    bfs_al_categoria_filtro(lista_recetas, 0, tipo)
    bfs_al_eliminar_ingrediente(lista_recetas, 0, alimento)
    lista = bfs_Get_lista(lista_recetas, 0)
    list_json = convert_json(lista)
    return jsonify(list_json)

if __name__ == '__main__':
    app.run()

if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1', port=5000)