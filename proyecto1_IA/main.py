import threading
import time
from grid import Grid
import networkx as nx
import matplotlib.pyplot as plt
import tkinter
from tkinter import PhotoImage, filedialog

# Esta función lee el archivo que contiene la matriz Y retorna una 
# lista de listas, donde cada sub lista es un renglón del archivo de texto.
def read(ruta_archivo):
    lineas = []
    with open(ruta_archivo, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            lineas.append(linea)
    return lineas

# Esta función recibe como parámetro una lista de listas y retorna una matriz.
def crear_matriz(lista):
    length = len(lista)
    matriz = Grid(length, length) # Se crea una instancia de la clase Grid.
    row = 0
    for linea in lista:
        linea = str(linea).split()
        column = 0
        for item in linea:
            matriz[row][column] = item
            column += 1
        row += 1
    return matriz

# Esta función recibe como parámetro la matriz, el punto de partida y el punto de llegada.
# El método ord() retorna el código ASCII de un carácter, las letras mayúsculas van desde 
# el número 65 hasta el 90, al restar 65 a la letra ingresada se obtine la fila que le corresponde 
# dentro de la matriz. 
def ruta(matriz, start, end):
    ini = (ord(start) - 65)
    fin = (ord(end) - 65)
    nodo = matriz.__getitem__(ini)[fin] # Se consulta la letra almacenada en la matriz.
    if nodo == "-":
        return "NoCamino"
    else:
        camino = []
        camino.append(ini)
        # Mientras que los puntos analizados no sean la meta, el while almacenara 
        # los puntos por donde pasa para posteriormente indicar la ruta.
        while nodo != "-": 
            new_ini = (ord(nodo.upper()) - 65)
            camino.append(new_ini)
            nodo = matriz.__getitem__(new_ini)[fin]
        for i in range(len(camino)):
            camino[i] = chr(camino[i] + 65)
        return camino

# Esta función recibe como parámetro la matriz.
# Como la cantidad de nodos es igual a la cantidad de columnas con el método len() 
# a una fila obtengo la cantidad de nodos.
def nodes_and_edges(matriz):
    num_nodos = len(matriz.__getitem__(0))
    lista_nodos = list() # Lista que almacenara los nodos del grafo.
    lista_adyacentes = list() # Lista que almacenara las aristas del grafo.
    for i in range(num_nodos):
        letra_ini = chr(i + 65) # Convierte el número de la fila a su correspondiente letra.
        lista_nodos.append(letra_ini)
        fila = matriz.__getitem__(i)
        for col in fila:
            if col != "-":
                union = letra_ini + col
                union_inv = union[::-1] # Se invierte la cadena de caracteres almacena en unión (Ej: hola -> aloh).
                # Como la arista AB es la misma BA entonces este if evita que se repitan aristas.
                if not(union in lista_adyacentes or union_inv in lista_adyacentes):
                    lista_adyacentes.append(union)
    
    lista_nodes_and_edges = list()
    lista_nodes_and_edges.append(lista_nodos)
    lista_nodes_and_edges.append(lista_adyacentes)
    return lista_nodes_and_edges

# El programa para ir mostrando los nodos que debe seguir el agente lo que hace es actualizar la venta 
# tantas veces nodos tenga que pasar, cada vez que itera pinta el nodo siguiente hasta terminar, 
# cuando ya llega a meta muestra todo el grafo con los nodos pintados por donde debe ir.
def draw_mapa(lista_nodos, lista_adyacentes, camino, contador, iterando):
    if iterando == True:
        G = nx.Graph()
        # Agrega los nodos al grafo.
        for nodo in lista_nodos:
            G.add_node(nodo)
        # Agrega las aristas al grafo.
        for edge in lista_adyacentes:
            G.add_edge(edge[0], edge[1])
        
        lista_nodos_color = list() # Esta lista contiene los nodos que deben pintarse en cada una de las iteraciones.
        color = list() # Esta lista contiene todos los nodos del grafo, cada uno con su respectivo color.

        if contador > 0:
            for i in range(contador):
                lista_nodos_color.append(camino[i])
            # Si el nodo está en la lista lista_nodos_color es porque este nodo debe pintarse en la iteración actual.
            for node in lista_nodos:
                if node in lista_nodos_color:
                    color.append('red')
                else:
                    color.append('blue')

            nx.draw(G, with_labels=True, pos=nx.circular_layout(G), node_color=color)
            plt.show()
        else:
            nx.draw(G, with_labels=True, pos=nx.circular_layout(G)) # En la primera iteración no se pintan los nodos.
            plt.show()
    else:
        print("No estoy iterando")
        G = nx.Graph()

        for nodo in lista_nodos:
            G.add_node(nodo)
        
        for edge in lista_adyacentes:
            G.add_edge(edge[0], edge[1])
        
        lista_nodos_color = list()
        color = list()

        for i in range(contador):
            lista_nodos_color.append(camino[i])
        
        for node in lista_nodos:
            if node in lista_nodos_color:
                color.append('red')
            else:
                color.append('blue')

        nx.draw(G, with_labels=True, pos=nx.circular_layout(G), node_color=color)
        plt.show()

# el método show() de la clase pyplot muestra una ventana con el grafo, pero este interrumpe la ejecución del programa, 
# para evitar este problema se ejecuta el método draw_mapa() en un hilo y se pausa por 3 segundos para que el 
# usuario pueda ver el paso a paso del recorrido que debe seguir.
def draw_camino_mapa(camino_seguir, matriz):
    listas = nodes_and_edges(matriz)

    for i in range(len(camino_seguir) + 1):
        t = threading.Thread(target=draw_mapa, args=(listas[0], listas[1], camino_seguir, i, True))
        t.start()
        time.sleep(3)
        plt.close('all')
    # Al finalizar las iteraciones el método draw_mapa() se ejecuta en el hilo principal para evitar que se cierre.
    draw_mapa(listas[0], listas[1], camino_seguir, len(camino_seguir), False)

# Alerta que se mostrara en caso de que los campos de texto estén vacíos.
def alerta(msj):
    alert = tkinter.Toplevel(ventana)
    alert.geometry("240x40")
    alert.title("Alerta")
    lb_alerta = tkinter.Label(alert, text = msj, fg="red")
    lb_alerta.place(x=10, y=10)
    x = ventana.winfo_x()
    y = ventana.winfo_y()
    alert.geometry("+%d+%d" % (x + 30, y + 50))
    
def ejecutar_busqueda():
    # Se obtiene los nodos de partida y de llegada de los campos de texto.
    start = str(tb_inicio.get().strip().upper())
    end = str(tb_fin.get().strip().upper())

    if start == "":
        alerta("Error, debes agregar un punto de partida.")
        return
    
    if end == "":
        alerta("Error, debes agregar un punto de llegada.")
        return

    # se ejecuta el explorador de archivos para que el usuario seleccione el archivo de texto con la matriz.
    ruta_del_archivo = filedialog.askopenfilename(title="Abrir", initialdir="c:")

    # se cierra la GUI pues no se interactuará más con ella.
    ventana.destroy()

    lista =  read(ruta_del_archivo)
    matriz = crear_matriz(lista)
    camino_seguir = ruta(matriz, start, end)
    if camino_seguir == "NoCamino":
        print("Felicidades, no debes seguir ninguna ruta, ya estás en tu destino.")
    else:
        print(camino_seguir)
        # El método draw_camino_mapa() se ejecuta en otro hilo para que no interrumpa con la ejecución del mainloop() 
        # de la GUI, ambos no se pueden ejecutar en el hilo principal.
        te = threading.Thread(target=draw_camino_mapa, args=(camino_seguir, matriz))
        te.start()

# Creación de la interfaz gráfica.
ventana = tkinter.Tk()
ventana.title("Waypoint navigation")
ventana.geometry("300x150")
ventana.eval('tk::PlaceWindow . center')

lb_inicio = tkinter.Label(ventana, text="Escribe el punto de partida:")
lb_inicio.place(x=10, y=10)

tb_inicio = tkinter.Entry(ventana, width=25)
tb_inicio.place(x=13, y=33)

lb_fin = tkinter.Label(ventana, text="Escribe el punto de llegada:")
lb_fin.place(x=10, y=56)

tb_fin = tkinter.Entry(ventana, width=25)
tb_fin.place(x=13, y=79)

btn_ejecutar = tkinter.Button(ventana, text="Buscar archivo", command=ejecutar_busqueda, width=20)
btn_ejecutar.place(x=15, y=109)

imagen = PhotoImage(file="ImgNavigationX64.png")
lb_imagen = tkinter.Label(ventana, image=imagen)
lb_imagen.place(x=200, y=40)

def main():
    ventana.mainloop()

if __name__ == "__main__":
    main()
