import sys
import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk, Image
from random import choice, randint
import os

class Ahorcado():
    # Variable de clase para persistir puntos entre instancias
    puntuacion_total = 0
    record = 0

    def __init__(self, root):
        self.root = root
        self.configurar_ventana()
        self.inicializar_recursos()
        self.inicializar_juego()
        self.crear_interfaz()
        self.actualizar_estado()
        
    def configurar_ventana(self):
        """Configuración inicial de la ventana principal"""
        self.root.title("Adivina la Palabra - Ahorcado")
        self.root.resizable(0, 0)
        self.root.config(bg='gray95')

    def inicializar_recursos(self):
        """Carga imágenes y palabras necesarias para el juego"""
        self.imagenes_ahorcado = self.cargar_imagenes()
        self.palabras_por_longitud = self.cargar_palabras()

    def inicializar_juego(self):
        """Inicializa variables para una nueva partida"""
        self.vidas = 8
        self.puntuacion_actual = 0
        self.puntos_para_revelar = 100
        self.juego_activo = True
        self.letras_reveladas = 0
        self.etapa_ahorcado = 0
        self.letras_intentadas = set()
        self.longitud_palabra = randint(5, 10)
        self.palabra_actual = choice(self.palabras_por_longitud[self.longitud_palabra]).upper()
        self.letras_adivinadas = ['_' for _ in self.palabra_actual]
        self.puntos_gastados_revelar = 0
        
    def cargar_imagenes(self):
        """Carga las 7 imágenes del ahorcado (0-6)"""
        imagenes = []
        try:
            for i in range(9):
                ruta = f'recursos/imagenes/ahorcado_{i}.png'
                img = Image.open(ruta).resize((300, 300), Image.LANCZOS)
                imagenes.append(ImageTk.PhotoImage(img))
        except FileNotFoundError as e:
            messagebox.showerror("Error", f"Archivo no encontrado: {e.filename}")
            sys.exit(1)
        return imagenes
    
    def cargar_palabras(self):
        """Carga las palabras desde archivos organizados por longitud"""
        palabras = {}
        # Cargar archivos de palabras
        for longitud in range(5, 11):
            archivo = f'recursos/palabras/palabras_adivinar_{longitud}.txt'
            if not os.path.exists(archivo):
                messagebox.showerror("Error", f"Archivo no encontrado: {archivo}")
                sys.exit(1)

            # Leer palabras del archivo
            with open(archivo, 'r', encoding='utf-8') as f:
                palabras[longitud] = [line.strip().upper() for line in f if line.strip()]
        return palabras
    
    def crear_interfaz(self):
        """Construye todos los componentes de la interfaz gráfica"""
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
        
        self.label_vidas = tk.Label(self.panel_estado, text=f'Vidas: {self.vidas}', font=('Arial', 12), bg='gray80')
        self.label_vidas.pack(side=tk.LEFT, padx=10)

        self.label_puntos = tk.Label(self.panel_estado, text=f'Puntos: {self.puntuacion_actual} (Total: {Ahorcado.puntuacion_total})', font=('Arial', 12), bg='gray80')
        self.label_puntos.pack(side=tk.LEFT, padx=10)

        self.label_record = tk.Label(self.panel_estado, text=f'Récord: {Ahorcado.record}', font=('Arial', 12), bg='gray80')
        self.label_record.pack(side=tk.LEFT, padx=10)
        
        self.btn_revelar = tk.Button(self.panel_estado, text=f'Revelar letra ({self.puntos_para_revelar} pts)', command=self.revelar_letra, state=tk.DISABLED)
        self.btn_revelar.pack(side=tk.LEFT, padx=10)
        
        # Botón Reiniciar (siempre visible)
        self.btn_reiniciar = tk.Button(
            self.panel_estado, 
            text='Reiniciar', 
            command=lambda: self.reiniciar(reset_puntos=True)
        )
        self.btn_reiniciar.pack(side=tk.LEFT, padx=10)
        
        # Botón Salir (siempre visible)
        self.btn_salir = tk.Button(self.panel_estado, text='Salir', command=self.root.destroy)
        self.btn_salir.pack(side=tk.LEFT, padx=10)
        
        # Panel de la palabra oculta
        self.panel_palabra = tk.Frame(self.marco_principal, bg='gray95')
        self.panel_palabra.grid(row=2, column=0, columnspan=2, pady=20)
        self.crear_labels_palabra()

        # Teclado virtual
        self.panel_teclado = tk.Frame(self.marco_principal)
        self.panel_teclado.grid(row=3, column=0, columnspan=2, pady=10)
        self.crear_teclado()

    def crear_labels_palabra(self):
        """Crea los labels para mostrar la palabra oculta"""
        self.labels_letras = []
        for letra in self.palabra_actual:
            label = tk.Label(self.panel_palabra, text='_', font=('Arial', 24), width=3, bg='gray95')
            label.pack(side=tk.LEFT, padx=5)
            self.labels_letras.append(label)
            
    def crear_teclado(self):
        """Crea el teclado virtual con las letras del abecedario"""
        teclas = ['QWERTYUIOP', 'ASDFGHJKLÑ', 'ZXCVBNM']
        self.botones = {}
        
        for fila, letras in enumerate(teclas):
            marco = tk.Frame(self.panel_teclado)
            marco.pack()
            for letra in letras:
                btn = tk.Button(marco, text=letra, width=4, height=2,command=lambda l=letra: self.intentar_letra(l))
                btn.pack(side=tk.LEFT, padx=2, pady=2)
                self.botones[letra] = btn
    
    def mostrar_ahorcado(self):
        """Muestra la imagen correspondiente a los errores actuales"""
        if 0 <= self.etapa_ahorcado < len(self.imagenes_ahorcado):
            self.label_imagen.config(image=self.imagenes_ahorcado[self.etapa_ahorcado])
            self.label_imagen.image = self.imagenes_ahorcado[self.etapa_ahorcado]

    def actualizar_estado(self):
        """Actualiza todos los elementos de la interfaz"""
        self.mostrar_ahorcado()
        self.label_vidas.config(text=f'Vidas: {self.vidas}')
        self.label_puntos.config(text=f'Puntos: {self.puntuacion_actual} (Total: {Ahorcado.puntuacion_total})')
        self.btn_revelar.config(
            text=f'Revelar letra ({self.puntos_para_revelar} pts)',
            state=tk.NORMAL if (self.puntuacion_actual + Ahorcado.puntuacion_total) >= self.puntos_para_revelar 
            else tk.DISABLED
        )
        # Actualizar letras adivinadas
        for i, letra in enumerate(self.palabra_actual):
            if self.letras_adivinadas[i] != '_':
                self.labels_letras[i].config(text=letra)
    
    def intentar_letra(self, letra):
        """Maneja el evento de intentar una letra"""
        if not self.juego_activo:
            return
            
        letra = letra.upper()
        self.botones[letra].config(state=tk.DISABLED)
        self.letras_intentadas.add(letra)
        
        if letra in self.palabra_actual:
            self.manejar_acierto(letra)
        else:
            self.manejar_error()
            
    def manejar_acierto(self, letra):
        """Lógica cuando se acierta una letra"""
        self.puntuacion_actual += 20

        for i, l in enumerate(self.palabra_actual):
            if l == letra:
                self.letras_adivinadas[i] = letra
                
        self.actualizar_estado()
                
        if '_' not in self.letras_adivinadas:
            self.ganar()
            
    def manejar_error(self):
        """Lógica cuando se comete un error"""
        self.vidas -= 1
        self.etapa_ahorcado += 1
        if self.vidas == 0:
            self.perder()
        else:
            self.actualizar_estado()
    
    def revelar_letra(self):
        """Revela una letra usando puntos acumulados"""
        if (self.puntuacion_actual + Ahorcado.puntuacion_total) >= self.puntos_para_revelar:
            ocultas = [i for i, letra in enumerate(self.letras_adivinadas) if letra == '_']
            if ocultas:
                idx = choice(ocultas)
                letra = self.palabra_actual[idx]
                self.letras_adivinadas[idx] = letra
                
                # Descontar puntos de la partida actual primero
                if self.puntuacion_actual >= self.puntos_para_revelar:
                    self.puntuacion_actual -= self.puntos_para_revelar
                else:
                    # Si no alcanzan los puntos actuales, usar los acumulados
                    Ahorcado.puntuacion_total -= (self.puntos_para_revelar - self.puntuacion_actual)
                    self.puntuacion_actual = 0
                    
                self.puntos_para_revelar += 50
                self.letras_reveladas += 1
                
                self.actualizar_estado()

                if '_' not in self.letras_adivinadas:
                    self.ganar()                    
    
    def bloquear_teclado(self, bloquear):
        """Bloquea o desbloquea el teclado"""
        estado = tk.DISABLED if bloquear else tk.NORMAL
        for letra, boton in self.botones.items():
            boton.config(state=estado)
    
    def ganar(self):
        """Maneja la victoria del jugador"""
        self.actualizar_estado()
        self.juego_activo = False
        # Calcular puntos finales
        bono_vidas = self.vidas * 40
        puntos_partida = self.puntuacion_actual + bono_vidas
        Ahorcado.puntuacion_total += puntos_partida
        Ahorcado.record += puntos_partida

        mensaje = (
            f'¡Felicidades! Ganaste:\n'
            f'La palabra era: {self.palabra_actual}\n'
            f'Bonus por vidas: {bono_vidas}\n'
            f'Puntos acumulados: {Ahorcado.puntuacion_total}\n'
            f'Récord: {Ahorcado.record}\n\n'
            '¿Jugar de nuevo?'
        )
        
        if messagebox.askyesno('¡Ganaste!', mensaje):
            self.reiniciar(reset_puntos=False)
        else:
            self.root.destroy()
    
    def perder(self):
        """Maneja la derrota del jugador"""
        self.juego_activo = False
        self.bloquear_teclado(True)
        # Mostrar palabra completa
        for i in range(len(self.palabra_actual)):
            self.letras_adivinadas[i] = self.palabra_actual[i]
        self.actualizar_estado()

        mensaje = (
            f'¡Game Over!\n'
            f'La palabra era: {self.palabra_actual}\n'
            f'Récord: {Ahorcado.record}\n\n'
            '¿Jugar de nuevo?'
        )
        
        if messagebox.askyesno('¡Perdiste!', mensaje):
            self.reiniciar(reset_puntos=True)
        else:
            self.root.destroy()
    
    def reiniciar(self, reset_puntos=False):
        """Reinicia el juego, opcionalmente reseteando puntos"""
        if reset_puntos:
            Ahorcado.puntuacion_total = 0  # Solo resetea si es un reinicio manual o se pierde
            Ahorcado.record = 0
        
        # Destruye la ventana actual y crea una nueva
        self.root.destroy()
        nueva_ventana = tk.Tk()
        Ahorcado(nueva_ventana)
        nueva_ventana.mainloop()

if __name__ == '__main__':
    root = tk.Tk()
    juego = Ahorcado(root)
    root.mainloop()