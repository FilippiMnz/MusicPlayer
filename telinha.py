from tkinter import *
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import pygame
from pygame import mixer
import os
import time
from mutagen.mp3 import MP3
from tkinter import PhotoImage
import random
import yt_dlp

mixer.init()
musicas = []
indice_musica_atual = -1
caminho_diretorio = '#############################'
musica_pausada = False
tempo_inicial = 0
loop_ativado = False
shuffle_ativado = False
pygame.init()

resultados_busca = []

def buscar_musicas_youtube(query):
    global resultados_busca
    options = {
        'format': 'bestaudio/best',
        'default_search': 'ytsearch10:',
        'extract_flat': True,
        'quiet': True,
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        try:
            resultados = ydl.extract_info(f"ytsearch10:{query}", download=False)
            if resultados and 'entries' in resultados:
                resultados_busca = resultados['entries']
                return resultados_busca
            else:
                return []
        except Exception as e:
            print(f"Erro ao buscar músicas: {e}")
            return []

def hook_progresso(d):
    if d['status'] == 'downloading':
        progresso = float(d['downloaded_bytes']) / float(d['total_bytes']) * 100
        barra_download['value'] = progresso
        janela.update_idletasks()

def baixar_musica_selecionada(url):
    options = {
        'format': 'bestaudio/best',
        'outtmpl': f'{caminho_diretorio}/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'progress_hooks': [hook_progresso], 
    }

    with yt_dlp.YoutubeDL(options) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
            nome_arquivo = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
            print(f"Música baixada: {nome_arquivo}")
            carregar_musicas_do_diretorio()  
        except Exception as e:
            print(f"Erro ao baixar a música: {e}")
        finally:
            barra_download['value'] = 0  


def exibir_resultados_busca():
    query = entrada_pesquisa.get()
    if not query:
        return

    resultados = buscar_musicas_youtube(query)
    lista_resultados.delete(0, tk.END)  

    for resultado in resultados:
        lista_resultados.insert(tk.END, resultado['title'])

def baixar_musica_selecionada_da_lista():
    global resultados_busca
    selecionado = lista_resultados.curselection()
    if not selecionado:
        return

    indice = selecionado[0]
    url = f"https://www.youtube.com/watch?v={resultados_busca[indice]['id']}"
    baixar_musica_selecionada(url)

def carregar_musicas_do_diretorio():
    global indice_musica_atual, musicas, caminho_diretorio
    if not os.path.exists(caminho_diretorio):
        print(f"Diretório não encontrado: {caminho_diretorio}")
        return
    musicas = [f for f in os.listdir(caminho_diretorio) if f.lower().endswith(('.mp3', '.wav'))]
    if not musicas:
        print("Nenhuma música encontrada no diretório.")
        return
    print(f"Músicas encontradas: {musicas}")
    indice_musica_atual = 0

    lista_musicas.delete(0, tk.END)
    for musica in musicas:
        lista_musicas.insert(tk.END, musica)

    tocar_musica()

def tocar_musica():
    global indice_musica_atual, musicas, caminho_diretorio, musica_pausada, tempo_inicial
    if 0 <= indice_musica_atual < len(musicas):
        caminho_completo = os.path.join(caminho_diretorio, musicas[indice_musica_atual])
        try:
            mixer.music.load(caminho_completo)
            mixer.music.play()
            musica_pausada = False
            tempo_inicial = time.time()
            exibir_imagem()
            atualizar_barra_progresso()
            atualizar_nome_musica()
            atualizar_tempo()
        except Exception as e:
            print(f"Erro ao carregar a música: {e}")

def atualizar_nome_musica():
    nome_musica = musicas[indice_musica_atual]
    nome_musica_sem_extensao = nome_musica.split('.')[0]
    nome.config(text=nome_musica_sem_extensao)

def pausar_ou_retomar_musica():
    global musica_pausada, tempo_inicial
    if musica_pausada:
        mixer.music.unpause()
        tempo_inicial = time.time() - tempo_inicial
        musica_pausada = False
    else:
        mixer.music.pause()
        musica_pausada = True

def ajustar_volume(valor):
    volume = float(valor) / 100
    mixer.music.set_volume(volume)

def proxima_musica():
    global indice_musica_atual
    if indice_musica_atual < len(musicas) - 1:
        indice_musica_atual += 1
        tocar_musica()

def musica_anterior():
    global indice_musica_atual
    if indice_musica_atual > 0:
        indice_musica_atual -= 1
        tocar_musica()

def exibir_imagem():
    caminho_imagem = 'default.jpg'
    if os.path.exists(caminho_imagem):
        try:
            imagem = Image.open(caminho_imagem)
            imagem = imagem.resize((200, 200))
            imagem_tk = ImageTk.PhotoImage(imagem)
            label_imagem.config(image=imagem_tk)
            label_imagem.image = imagem_tk
        except Exception as e:
            print(f'Erro ao carregar imagem: {e}')
    else:
        print('Imagem padrão não encontrada.')

def atualizar_barra_progresso():
    if mixer.music.get_busy():
        tempo_atual = time.time() - tempo_inicial
        tempo_total = obter_duracao_musica()
        progresso = (tempo_atual / tempo_total) * 100
        progresso_barra['value'] = progresso

        if progresso < 100:
            janela.after(1000, atualizar_barra_progresso)

def atualizar_tempo():
    if mixer.music.get_busy():
        tempo_atual = time.time() - tempo_inicial
        tempo_total = obter_duracao_musica()
        tempo_decorrido.config(text=f"{int(tempo_atual)}s / {int(tempo_total)}s")
        janela.after(1000, atualizar_tempo)

def obter_duracao_musica():
    global musicas, indice_musica_atual, caminho_diretorio
    caminho_completo = os.path.join(caminho_diretorio, musicas[indice_musica_atual])
    try:
        audio = MP3(caminho_completo)
        return audio.info.length
    except Exception as e:
        print(f"Erro ao obter duração da música: {e}")
        return 0

def style_button(button):
    button.config(
        font=("Helvetica", 10, "bold"),
        fg="white",
        bg="gray64",
        activebackground="white",
        relief="raised",
        padx=10,
        pady=5,
        highlightthickness=0,
        width=6
    )

def selecionar_musica(event):
    global indice_musica_atual
    selecionado = lista_musicas.curselection()
    if selecionado:
        indice_musica_atual = selecionado[0]
        tocar_musica()

def configurar_fim_da_musica():
    mixer.music.set_endevent(pygame.USEREVENT)

def verificar_fim_da_musica():
    for event in pygame.event.get():
        if event.type == pygame.USEREVENT:
            proxima_musica()
    janela.after(1000, verificar_fim_da_musica)

def alternar_loop():
    global loop_ativado
    loop_ativado = not loop_ativado
    print("Loop ativado" if loop_ativado else "Loop desativado")

def alternar_shuffle():
    global shuffle_ativado, musicas
    shuffle_ativado = not shuffle_ativado
    if shuffle_ativado:
        random.shuffle(musicas)
        print("Shuffle ativado")
    else:
        carregar_musicas_do_diretorio()
        print("Shuffle desativado")

mixer.init()
mixer.music.set_volume(0.5)

janela = tk.Tk()
janela.title('MUSIC')
janela.geometry('400x500')
janela.configure(bg='bisque2')

frame_superior = tk.Frame(janela, bg='bisque2')
frame_superior.pack(fill=tk.BOTH, expand=True)

label_imagem = tk.Label(frame_superior, bg='bisque2')
label_imagem.pack(pady=10)

nome = tk.Label(frame_superior, text="Nenhuma música", bg='bisque2')
nome.pack(pady=5)

progresso_barra = ttk.Progressbar(frame_superior, orient="horizontal", length=250, mode="determinate")
progresso_barra.pack(pady=10)

tempo_decorrido = tk.Label(frame_superior, text="0s / 0s", bg='bisque2')
tempo_decorrido.pack(pady=5)

frame_botoes = tk.Frame(frame_superior, bg='bisque2')
frame_botoes.pack(pady=20)

botao_esquerda = tk.Button(frame_botoes, text='◀', bg='gray64', command=musica_anterior)
style_button(botao_esquerda)
botao_esquerda.grid(row=0, column=0, padx=10)

botao_central = tk.Button(frame_botoes, text='⏯', bg='gray64', command=pausar_ou_retomar_musica)
style_button(botao_central)
botao_central.grid(row=0, column=1, padx=10)

botao_direita = tk.Button(frame_botoes, text='▶', bg='gray64', command=proxima_musica)
style_button(botao_direita)
botao_direita.grid(row=0, column=2, padx=10)

volume_scale = tk.Scale(frame_superior, from_=0, to=100, orient="horizontal", label="Volume", command=ajustar_volume)
volume_scale.set(50)
volume_scale.pack(pady=10)

frame_inferior = tk.Frame(janela, bg='bisque2')
frame_inferior.pack(fill=tk.BOTH, expand=True)

frame_lista_musicas = tk.Frame(frame_inferior, bg='bisque2')
frame_lista_musicas.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

label_musicas = tk.Label(frame_lista_musicas, text="Lista de Músicas", bg='bisque2')
label_musicas.pack(pady=5)

lista_musicas = tk.Listbox(frame_lista_musicas, bg='bisque2', selectmode=tk.SINGLE)
lista_musicas.pack(fill=tk.BOTH, expand=True)
lista_musicas.bind('<<ListboxSelect>>', selecionar_musica)

frame_pesquisa = tk.Frame(frame_inferior, bg='bisque2')
frame_pesquisa.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

entrada_pesquisa = tk.Entry(frame_pesquisa, width=30)
entrada_pesquisa.pack(pady=5)

botao_pesquisar = tk.Button(frame_pesquisa, text="Pesquisar", command=exibir_resultados_busca)
botao_pesquisar.pack(pady=5)

label_resultados = tk.Label(frame_pesquisa, text="Resultados da Busca", bg='bisque2')
label_resultados.pack(pady=5)

lista_resultados = tk.Listbox(frame_pesquisa, bg='bisque2', selectmode=tk.SINGLE)
lista_resultados.pack(fill=tk.BOTH, expand=True)

botao_baixar = tk.Button(frame_pesquisa, text="Baixar Música Selecionada", command=baixar_musica_selecionada_da_lista)
botao_baixar.pack(pady=5)

barra_download = ttk.Progressbar(frame_pesquisa, orient="horizontal", length=250, mode="determinate")
barra_download.pack(pady=10)

frame_inferior.grid_rowconfigure(0, weight=1)
frame_inferior.grid_columnconfigure(0, weight=1)
frame_inferior.grid_columnconfigure(1, weight=1)

carregar_musicas_do_diretorio()
janela.mainloop()
