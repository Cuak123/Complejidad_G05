import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from tkinter import ttk
from tkinter import messagebox
import graphviz as gv
import csv

from PIL import ImageTk, Image

from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
import mpl_toolkits as mpl
import os


class receta:
    def __init__(self, padre, id, nombre, tiempo, categoria, hijos, ingredientes):
        self.nombre = nombre
        self.tiempo = tiempo
        self.categoria = categoria
        self.id = id
        self.padre = padre
        self.hijos = hijos
        self.ingredientes = ingredientes


class VentanaPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Sugerencias")
        self.geometry("1200x600")

        self.label_pelicula = tk.Label(self, text="Ingrese el tiempo (ejemplo: 1h 30m):")
        self.label_pelicula.place(x=20, y=45)

        self.label_1 = tk.Label(self, text="Categoria:")
        self.label_1.place(x=900, y=45)

        self.label_2 = tk.Label(self, text="Ingredientes")
        self.label_2.place(x=600, y=45)

        self.entry_tiempo = tk.Entry(self)
        self.entry_tiempo.place(x=250, y=45)

        self.entry_ingredientes = tk.Entry(self)
        self.entry_ingredientes.place(x=690, y=45)

        self.boton_Actualizar = tk.Button(self, text="Actualizar", command=self.Actualizar_grafico)
        self.boton_Actualizar.place(x=450, y=40)

        # Crear tabla
        self.tabla = ttk.Treeview(self, columns=("ID", "Nombre", "Categoria","Tiempo"), show="headings")
        self.tabla.column("ID", width=50)
        self.tabla.column("Nombre", width=150)
        self.tabla.column("Categoria", width=150)
        self.tabla.column("Tiempo", width=50)

        self.tabla.heading("ID", text="ID")
        self.tabla.heading("Nombre", text="Nombre")
        self.tabla.heading("Categoria", text="Categoria")
        self.tabla.heading("Tiempo", text="Tiempo")

        # Crear scrollbar y asociarlo a la tabla
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscroll=scrollbar.set)

        # Posicionar la tabla y el scrollbar en la ventana
        self.tabla.place(x=550, y=130, width=600, height=450)
        scrollbar.place(x=1150, y=100, height=450)

        # Leer el archivo CSV y almacenarlo en un DataFrame
        df = pd.read_csv('dataset_recetas.csv', sep=";")

        # Convertir el DataFrame a un array de objetos
        self.data = df.to_dict('records')

        # Obtener una lista de directores únicos

        # Obtener una lista de géneros únicos (separados por ',')
        #self.generos = df['genres'].str.split(',').explode().apply(lambda x: x.strip()).unique().tolist()


        # Crear el combobox de géneros
        #self.combo_generos = ttk.Combobox(self)
        #self.combo_generos['values'] = self.generos
        #self.combo_generos.place(x=690, y=45)

        # Crear el combobox de directores
        #self.combo_Categorias = ttk.Combobox(self, width=28)
        #self.combo_Categorias['values'] = self.Categorias
        #self.combo_Categorias.place(x=980, y=45)


        self.Check_Aperitivos = ttk.Checkbutton(self, text = "Aperitivos y tapas")
        self.Check_Aperitivos.place(x=980, y=10)

        self.Check_Aves = ttk.Checkbutton(self, text = "Aves y caza")
        self.Check_Aves.place(x=980, y=30)

        self.Check_Carnes = ttk.Checkbutton(self, text = "Carnes")
        self.Check_Carnes.place(x=980, y=50)

        self.Check_Arroz = ttk.Checkbutton(self, text = "Arroces y cereales")
        self.Check_Arroz.place(x=980, y=70)

        self.Check_Ensalada = ttk.Checkbutton(self, text = "Ensaladas")
        self.Check_Ensalada.place(x=980, y=90)

        self.canvas_grafo = tk.Canvas(self, width=500, height=450)
        self.canvas_grafo.place(x=20, y=100)

        self.canvas = None

        self.ListaReceta = self.Guardar_Datos_Lista()

        # CARGADO DE matriz de adyasencia
        #self.matriz = np.loadtxt('matrizAdy.csv', delimiter=',')

        # Crear un grafo de ejemplo
        self.Iniciar()
       
    
    def Iniciar(self):

        graph = self.drawDS()
        

        fig, ax = plt.subplots(figsize=(5, 5))
        pos = nx.spring_layout(graph)
        nx.draw(graph, pos, with_labels=True, node_size=1000, node_color='lightblue', edge_color='gray', font_size=8)
        plt.tight_layout()

        self.canvas = FigureCanvasTkAgg(fig, master=self.canvas_grafo)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

        toolbar = NavigationToolbar2Tk(self.canvas, self)
        toolbar.update()
        toolbar.place(x=20, y=510)

        
        self.actualizar_tabla(self.ListaReceta)

    def Actualizar_grafico(self):

        if self.canvas is not None:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
            self.ListaReceta = []
            lista_categorias = []
            self.ListaReceta = self.Guardar_Datos_Lista()

        tiempo = self.entry_tiempo.get()
        self.Buscar_receta_tiempo(tiempo)
        
        
        if self.Check_Aperitivos.instate(['selected']):
            lista_categorias.append("Recetas de Aperitivos y tapas")
        if self.Check_Aves.instate(['selected']):
            lista_categorias.append("Recetas de Aves y caza")
        if self.Check_Ensalada.instate(['selected']):
            lista_categorias.append("Recetas de Ensaladas")
        if self.Check_Arroz.instate(['selected']):
            lista_categorias.append("Recetas de Arroces y cereales")
        if self.Check_Carnes.instate(['selected']):
            lista_categorias.append("Recetas de Carne")

        print(lista_categorias)
        self.bfs_al_categoria_filtro(0, lista_categorias)

        ingrediente = self.entry_ingredientes.get()
        lista_ingre = ingrediente.split(",")
        self.bfs_al_eliminar_ingrediente(0,lista_ingre)

        graph = self.drawDS()

        fig, ax = plt.subplots(figsize=(5, 5))
        pos = nx.spring_layout(graph)
        nx.draw(graph, pos, with_labels=True, node_size=1000, node_color='lightblue', edge_color='gray', font_size=8)
        plt.tight_layout()

        self.canvas = FigureCanvasTkAgg(fig, master=self.canvas_grafo)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()
        
        self.bfs_al_actualizartabla(0)
        
    def bfs_al_actualizartabla(self, s):
        self.tabla.delete(*self.tabla.get_children())
        n = len(self.ListaReceta)
        visited = [False] * n
        queue = [s]
        visited[s] = True

        while queue:
            u = queue.pop(0)
            for v in self.ListaReceta[u].hijos:
                
                if not visited[v]:
                    visited[v] = True
                    item = self.ListaReceta[v]
                    self.tabla.insert("", "end", values=(item.id, item.categoria, item.nombre, item.tiempo))
                    queue.append(v)


    def Guardar_Datos_Lista(self):
        self.ListaReceta = []
        cont_id = 5
        nodo_vacio = receta(0,0,"","","",[], [])
        self.ListaReceta.append(nodo_vacio)
        nodo_vacio = receta(1,1,"","","Recetas de Aperitivos y tapas",[],[])
        self.ListaReceta.append(nodo_vacio)
        nodo_vacio = receta(2,2,"","","Recetas de Arroces y cereales",[],[])
        self.ListaReceta.append(nodo_vacio)
        nodo_vacio = receta(3,3,"","","Recetas de Aves y caza",[],[])
        self.ListaReceta.append(nodo_vacio)
        nodo_vacio = receta(4,4,"","","Recetas de Carne",[],[])
        self.ListaReceta.append(nodo_vacio)
        nodo_vacio = receta(5,5,"","","Recetas de Ensaladas",[],[])
        self.ListaReceta.append(nodo_vacio)

        with open('dataset_recetas.csv', 'r', encoding='utf-8') as archivo_csv:
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
                nueva_receta = receta(padre, id, nombre, tiempo, categoria, hijos, ingredientes)
                self.ListaReceta.append(nueva_receta)

        archivo_csv.close()
        return self.ListaReceta


    def drawDS(self):
        graph = nx.DiGraph()
        for e, p in enumerate(self.ListaReceta):
            graph.add_node(str(e))
            if p.padre != e:
                graph.add_edge(str(p.padre), str(e))
        return graph


    

    def actualizar_tabla(self, lista2):
        # Limpiar la tabla
        self.tabla.delete(*self.tabla.get_children())
        # Buscar objetos con ID igual a los elementos de la lista
        for i in lista2:
            # Agregar el objeto a la tabla
            self.tabla.insert("", "end", values=(i.id, i.categoria, i.nombre, i.tiempo))

    


    def bfs_al_categoria_filtro(self, s, list_categoria):
        print(list_categoria)
        n = len(self.ListaReceta)
        visited = [False] * n
        queue = [s]
        visited[s] = True

        while queue:
            u = queue.pop(0)
            print("Categoria")
            print(self.ListaReceta[u].hijos)
            auxlist = self.ListaReceta[u].hijos.copy()
            for v in auxlist:# 1 2 3 4 5
                print(str(v))
                if not visited[v]: # v = 3
                    visited[v] = True
                    print(self.ListaReceta[v].categoria)
                    if self.ListaReceta[v].categoria in list_categoria:
                        queue.append(v)
                        print("entra a la cola")
                    else:
                        self.ListaReceta[v].padre = v
                        self.ListaReceta[u].hijos.remove(v)
                        print(auxlist)
                        print("sale de los hijos")

    def bfs_al_eliminar_ingrediente(self, s, lista_ingredientes_eliminar):
        n = len(self.ListaReceta)
        visited = [False] * n
        queue = [s]
        visited[s] = True

       
        while queue:
            u = queue.pop(0)
            auxlist = self.ListaReceta[u].hijos.copy()
            for v in auxlist:
                if not visited[v]:
                    visited[v] = True
                    queue.append(v)
                    if (v not in [1, 2, 3, 4, 5]):
                        if (self.verificar_palabra_comun(lista_ingredientes_eliminar, self.ListaReceta[v].ingredientes)):
                            self.ListaReceta[v].padre = v
                            self.ListaReceta[u].hijos.remove(v)

    def verificar_palabra_comun(self, lista1, lista2):
        for ingrediente1 in lista1:
            palabras1 = ingrediente1.split()
            for ingrediente2 in lista2:
                palabras2 = ingrediente2.split()
                for palabra1 in palabras1:
                    for palabra2 in palabras2:
                        if palabra1.lower() == palabra2.lower():
                            return True
        return False

    def Buscar_receta_tiempo(self, tiempo_buscado):

        nodos_aperitivos = []
        nodos_arroces = []
        nodos_aves = []
        nodos_carne = []
        nodos_ensaladas = []

        for receta in self.ListaReceta:
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

        for i in range(0, len(nodos_aperitivos)):
            b = nodos_aperitivos[i]
            self.union(self.ListaReceta, b, self.ListaReceta[1].padre)
            self.ListaReceta[1].hijos.append(b)

        arroces_1 = nodos_arroces[0]
        for i in range(1, len(nodos_arroces)):
            b = nodos_arroces[i]
            self.union(self.ListaReceta, b, self.ListaReceta[2].padre)
            self.ListaReceta[2].hijos.append(b)

        aves_1 = nodos_aves[0]
        for i in range(1, len(nodos_aves)):
            b = nodos_aves[i]
            self.union(self.ListaReceta,b, self.ListaReceta[3].padre)
            self.ListaReceta[3].hijos.append(b)

        carne_1 = nodos_carne[0]
        for i in range(1, len(nodos_carne)):
            b = nodos_carne[i]
            self.union(self.ListaReceta, b, self.ListaReceta[4].padre)
            self.ListaReceta[4].hijos.append(b)

        ensalada_1 = nodos_ensaladas[0]
        for i in range(1, len(nodos_ensaladas)):
            b = nodos_ensaladas[i]
            self.union(self.ListaReceta, b, self.ListaReceta[5].padre)
            self.ListaReceta[5].hijos.append(b)

        self.union(self.ListaReceta, self.ListaReceta[1].padre, 0)
        self.union(self.ListaReceta, self.ListaReceta[2].padre, 0)
        self.union(self.ListaReceta, self.ListaReceta[3].padre, 0)
        self.union(self.ListaReceta, self.ListaReceta[4].padre, 0)
        self.union(self.ListaReceta, self.ListaReceta[5].padre, 0)

        self.ListaReceta[0].hijos.append(self.ListaReceta[1].id)
        self.ListaReceta[0].hijos.append(self.ListaReceta[2].id)
        self.ListaReceta[0].hijos.append(self.ListaReceta[3].id)
        self.ListaReceta[0].hijos.append(self.ListaReceta[4].id)
        self.ListaReceta[0].hijos.append(self.ListaReceta[5].id)

    def union(self, s, a, b):
        pa = self.find(s, a)
        #print(pa)
        pb = self.find(s, b)
        #print(pb)
        s[pa].padre = pb
        #print(s)

    def find(self, s, a):
        i = a
        while s[i].padre != i:
            i = s[i].padre
        return i


ventana_principal = VentanaPrincipal()
ventana_principal.mainloop()
