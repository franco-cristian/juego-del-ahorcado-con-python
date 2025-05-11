import sys
import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk, Image
from random import choice, randint
import os

class Ahorcado():
    def __init__(self, root):
        self.root = root
        self.root.title("Adivina la Palabra - Ahorcado")
        self.root.resizable(0, 0)
        self.root.config(bg='gray95')
        
        # Variables del juego
        self.vidas = 6
        self.puntuacion = 0
        self.puntos_para_revelar = 100
        self.juego_activo = True
        self.letras_reveladas = 0
        self.etapa_ahorcado = 0  # Controla qué imagen mostrar (0-6)
        
        # Cargar imágenes del ahorcado
        self.imagenes_ahorcado = self.cargar_imagenes()
        
        # Cargar palabras
        self.palabras = self.cargar_palabras()
        self.longitud_palabra = randint(5, 10)
        self.palabra_actual = choice(self.palabras).upper()
        self.letras_adivinadas = ['_' for _ in self.palabra_actual]
        self.letras_intentadas = set()
        
        # Configurar interfaz
        self.crear_interfaz()
        self.actualizar_estado()
        self.mostrar_ahorcado()
        
    def cargar_imagenes(self):
        """Carga las 7 imágenes del ahorcado (0-6)"""
        imagenes = []
        
        # Crear directorio si no existe
        if not os.path.exists('recursos/imagenes'):
            os.makedirs('recursos/imagenes')
            messagebox.showwarning("Advertencia", "Directorio de imágenes no encontrado. Se creará uno vacío.")
            return []
        
        # Cargar cada imagen
        for i in range(7):
            try:
                ruta = f'recursos/imagenes/ahorcado_{i}.png'
                img = Image.open(ruta)
                img = img.resize((300, 300), Image.LANCZOS)
                imagenes.append(ImageTk.PhotoImage(img))
            except FileNotFoundError:
                messagebox.showerror("Error", f"No se encontró la imagen: ahorcado_{i}.png")
                sys.exit(1)
                
        return imagenes
    
    def cargar_palabras(self):
        archivo = 'recursos/palabras/palabras_adivinar_5.txt'
        
        if not os.path.exists(archivo):
            messagebox.showerror("Error", f"No se encontró el archivo: {archivo}")
            sys.exit(1)

        with open(archivo, 'r', encoding='utf-8') as f:
            palabras = [line.strip().upper() for line in f.readlines() if line.strip()]
        
        return palabras

    
    def crear_interfaz(self):
        # Marco principal
        self.marco_principal = tk.Frame(self.root, bg='gray95')
        self.marco_principal.pack(padx=20, pady=10)
        
        # Panel del ahorcado (imagen)
        self.panel_ahorcado = tk.Frame(self.marco_principal, bg='gray95')
        self.panel_ahorcado.grid(row=0, column=0, columnspan=2, pady=10)
        
        self.label_imagen = tk.Label(self.panel_ahorcado, bg='white')
        self.label_imagen.pack()
        
        # Panel de estado
        self.panel_estado = tk.Frame(self.marco_principal, bg='gray80')
        self.panel_estado.grid(row=1, column=0, columnspan=2, pady=10, sticky='ew')
        
        self.label_vidas = tk.Label(self.panel_estado, text=f'Vidas: {self.vidas}', 
                                  font=('Arial', 12), bg='gray80')
        self.label_vidas.pack(side=tk.LEFT, padx=10)
        
        self.label_puntos = tk.Label(self.panel_estado, text=f'Puntos: {self.puntuacion}', 
                                   font=('Arial', 12), bg='gray80')
        self.label_puntos.pack(side=tk.LEFT, padx=10)
        
        self.btn_revelar = tk.Button(self.panel_estado, text=f'Revelar letra ({self.puntos_para_revelar} pts)',
                                    command=self.revelar_letra, state=tk.DISABLED)
        self.btn_revelar.pack(side=tk.LEFT, padx=10)
        
        # Botón Reiniciar (siempre visible)
        self.btn_reiniciar = tk.Button(self.panel_estado, text='Reiniciar',
                                     command=self.reiniciar)
        self.btn_reiniciar.pack(side=tk.LEFT, padx=10)
        
        # Botón Salir (siempre visible)
        self.btn_salir = tk.Button(self.panel_estado, text='Salir',
                                 command=self.root.destroy)
        self.btn_salir.pack(side=tk.LEFT, padx=10)
        
        # Panel de palabra
        self.panel_palabra = tk.Frame(self.marco_principal, bg='gray95')
        self.panel_palabra.grid(row=2, column=0, columnspan=2, pady=20)
        
        self.labels_letras = []
        for letra in self.palabra_actual:
            label = tk.Label(self.panel_palabra, text='_', font=('Arial', 24), 
                           width=3, bg='gray95')
            label.pack(side=tk.LEFT, padx=5)
            self.labels_letras.append(label)
        
        # Panel de teclado
        self.panel_teclado = tk.Frame(self.marco_principal)
        self.panel_teclado.grid(row=3, column=0, columnspan=2, pady=10)
        
        teclas = [
            'QWERTYUIOP',
            'ASDFGHJKLÑ',
            'ZXCVBNM'
        ]
        
        self.botones = {}
        for fila, letras in enumerate(teclas):
            marco_fila = tk.Frame(self.panel_teclado)
            marco_fila.pack()
            for letra in letras:
                btn = tk.Button(marco_fila, text=letra, width=4, height=2,
                              command=lambda l=letra: self.intentar_letra(l))
                btn.pack(side=tk.LEFT, padx=2, pady=2)
                self.botones[letra] = btn
    
    def mostrar_ahorcado(self):
        """Muestra la imagen correspondiente a la etapa actual del ahorcado"""
        if 0 <= self.etapa_ahorcado < len(self.imagenes_ahorcado):
            self.label_imagen.config(image=self.imagenes_ahorcado[self.etapa_ahorcado])
            self.label_imagen.image = self.imagenes_ahorcado[self.etapa_ahorcado]
    
    def actualizar_estado(self):
        self.label_vidas.config(text=f'Vidas: {self.vidas}')
        self.label_puntos.config(text=f'Puntos: {self.puntuacion}')
        self.btn_revelar.config(text=f'Revelar letra ({self.puntos_para_revelar} pts)',
                              state=tk.NORMAL if self.puntuacion >= self.puntos_para_revelar else tk.DISABLED)
        
        # Actualizar letras adivinadas
        for i, letra in enumerate(self.palabra_actual):
            if self.letras_adivinadas[i] != '_':
                self.labels_letras[i].config(text=letra)
    
    def intentar_letra(self, letra):
        if not self.juego_activo:
            return
            
        letra = letra.upper()
        self.botones[letra].config(state=tk.DISABLED)
        self.letras_intentadas.add(letra)
        
        if letra in self.palabra_actual:
            self.puntuacion += 20
            for i, l in enumerate(self.palabra_actual):
                if l == letra:
                    self.letras_adivinadas[i] = letra
            self.actualizar_estado()
            
            if '_' not in self.letras_adivinadas:
                self.ganar()
        else:
            self.vidas -= 1
            self.etapa_ahorcado += 1
            self.mostrar_ahorcado()
            self.actualizar_estado()
            if self.vidas == 0:
                self.perder()
    
    def revelar_letra(self):
        if self.puntuacion >= self.puntos_para_revelar and self.juego_activo:
            ocultas = [i for i, letra in enumerate(self.letras_adivinadas) if letra == '_']
            if ocultas:
                idx = choice(ocultas)
                letra = self.palabra_actual[idx]
                self.letras_adivinadas[idx] = letra
                self.puntuacion -= self.puntos_para_revelar
                self.puntos_para_revelar += 50
                self.letras_reveladas += 1
                self.actualizar_estado()
                
                if '_' not in self.letras_adivinadas:
                    self.ganar()
    
    def bloquear_teclado(self, bloquear):
        estado = tk.DISABLED if bloquear else tk.NORMAL
        for letra, boton in self.botones.items():
            boton.config(state=estado)
    
    def ganar(self):
        self.juego_activo = False
        self.puntuacion += self.vidas * 50
        self.bloquear_teclado(True)
        respuesta = messagebox.askyesno(
            '¡Ganaste!',
            f'Puntuación: {self.puntuacion}\n¿Quieres jugar de nuevo?'
        )
        self.reiniciar() if respuesta else self.root.destroy()
    
    def perder(self):
        self.juego_activo = False
        for i, letra in enumerate(self.palabra_actual):
            self.letras_adivinadas[i] = letra
        self.actualizar_estado()
        self.bloquear_teclado(True)
        respuesta = messagebox.askyesno(
            '¡Perdiste!',
            f'La palabra era: {self.palabra_actual}\n¿Quieres jugar de nuevo?'
        )
        self.reiniciar() if respuesta else self.root.destroy()
    
    def reiniciar(self):
        self.root.destroy()
        nueva_ventana = tk.Tk()
        Ahorcado(nueva_ventana)
        nueva_ventana.mainloop()

if __name__ == '__main__':
    root = tk.Tk()
    juego = Ahorcado(root)
    root.mainloop()