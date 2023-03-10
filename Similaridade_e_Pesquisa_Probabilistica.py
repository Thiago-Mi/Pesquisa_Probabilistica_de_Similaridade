#Biblioteca para utilzar a interface
from asyncio.windows_events import NULL
from math import log
import os
import tkinter as tk
from tkinter import  DISABLED, END, MULTIPLE, filedialog
import json 

#Bibliotecas para utilzar o arquivo html
import unicodedata
import re
from bs4 import BeautifulSoup
import nltk
from collections import Counter
from nltk.tokenize import RegexpTokenizer
nltk.download('stopwords')


LISTA_DE_PALAVRAS = []
DICIONARIO = {}
matriz_busca_global = []
matriz_pesquisa_global = {}


def removerCaracteresEspeciais(pal):
    palavraSemCaracteresEspeciais = unicodedata.normalize(u'NFKD', pal).encode('ascii', 'ignore').decode('utf8')
    return palavraSemCaracteresEspeciais

def construirDicionario(DICIONARIO):
    lines = {}
    excessao =0
    try:
        if excessao == 0:
            with open("arquivo_dicionario.json","w") as arquivo:
                lines.update(DICIONARIO)
                json.dump(lines,arquivo,indent=4)
                arquivo.close()
    except:
        print("Arquivo não foi gerado.")

def carregarDicionario():
    dicionario_carregado = {}
    with open("arquivo_dicionario.json","r") as arquivo:
        dicionario_carregado = json.load(arquivo)
    return dicionario_carregado

try:
    DICIONARIO = carregarDicionario() 
except:
    print("Nenhum dicionario adicionado")


#contabiliza quantos dos termos pesquisados existem nos arquivos adicionados. 
    contador_ni = 0
def contabilizar_termo(dicionario_atualizado : dict, pesquisa : str): 
    for dicionario_id, dicionario_info in dicionario_atualizado.items():
        for key in dicionario_info:
                if key == pesquisa:
                    contador_ni = contador_ni + 1
    return contador_ni


#contabiliza quantos dos termos pesquisados existem nos arquivos adicionados. 
def contabilizar_maxima_freq(dicionario_atualizado : dict): 
    contador_max = []
    linha = 0
    for dicionario_id, dicionario_info in dicionario_atualizado.items():
        for key in dicionario_info:
            if dicionario_info[key] < 200:
                if linha == 0:
                    linha = dicionario_info[key]
                elif linha < dicionario_info[key]:
                    linha = dicionario_info[key]
        contador_max.append(linha)
        linha = 0
    return contador_max

#calcula utilizando a similaridade 
def calculo_similaridade_simples(freq: int,peso:float):
    if freq>=1:
        similaridade = 1*peso
    else:
        similaridade=0
    return similaridade

def calculo_similaridade_completa(a,b):
    
    similaridade = log(a/b)

    return similaridade

def gerar_similaridade_completa(dicionario_atualizado):
    
    global matriz_busca_global
    global matriz_pesquisa_global
    similaridade_completa = []
    r = []
    num = []
    aux = []
    N = len(contabilizar_maxima_freq(dicionario_atualizado)) + 1
    lista_selecionados = selecao_itens_listbox()
    R = len(lista_selecionados)
    # limparCampo(listbox)
    for item in matriz_busca_global:
        for n in item:
            if n!=item[0]:
                if n > 0:
                    aux.append(n - 0.1)
                else:
                    aux.append(0)
        r.append(aux)
        aux = []
    for pesquisa in matriz_pesquisa_global:
        num.append(contabilizar_termo(dicionario_atualizado,pesquisa))

    arquivo =0
    for termo in r:
        i=0
        calculo =0
        aux = []
        arquivo+=1
        aux.append(arquivo)
        for idf in termo:
            
            if idf != 0:
                div1 = idf*(N-R-num[i]+idf)
                div2 = (num[i]-idf)*(R-idf)
                if div1!=0:
                    calculo += calculo_similaridade_completa(div1,div2)
            i+=1
        aux.append(calculo)
        similaridade_completa.append(aux)
    similaridade_completa = sorted(similaridade_completa, key=lambda item: item[1],reverse=True)
    limparCampo(listbox)
    for itens in similaridade_completa:
        listbox.insert(END,itens)
    return similaridade_completa

def gerar_similaridade_simples(dicionario_atualizado : dict, matriz_pesquisa : dict): 
    limparCampo(listbox)
    i = 0 
    matriz_busca = []
    linha = []
    similaridade = 0
    peso = {}
    aux = []
    similaridade_dicionario = []
    maxima_freq = contabilizar_maxima_freq(dicionario_atualizado)
    for dicionario_id, dicionario_info in dicionario_atualizado.items():
        linha=[]
        for matriz_pesquisa_info in matriz_pesquisa:
            if(len(peso) <= len(matriz_pesquisa.keys())-1):
                try:
                    peso[matriz_pesquisa_info] = log(len(maxima_freq)/contabilizar_termo(dicionario_atualizado,matriz_pesquisa_info),10)
                except:
                    peso[matriz_pesquisa_info] = 0
            for key in dicionario_info:
                if key == matriz_pesquisa_info:
                    if linha==[]:
                        # contador_ni = contabilizar_termo(dicionario_atualizado,key)
                        linha.append(int(dicionario_id))
                    similaridade = calculo_similaridade_simples(dicionario_info[key],peso[matriz_pesquisa_info])
                    linha.append(similaridade)
            if linha != []: 
                if similaridade == 0:
                    linha.append(0)   
                similaridade = 0

            else:
                linha.append(int(dicionario_id))
                linha.append(0)
                similaridade =0
        matriz_busca.append(linha)
        global matriz_busca_global
        matriz_busca_global = matriz_busca
    for item in matriz_busca:
        aux.append(item[0])
        aux.append(0)
        for n in item:
            if n!=item[0]:
                aux[1] += n
        if aux[1]>0:
            similaridade_dicionario.append(aux)
        aux = []
    return similaridade_dicionario


def limparCampo(campo):
    campo.delete(0,'end')

def selecao_itens_listbox():
    lista = []
    for i in listbox.curselection():
        lista.append(listbox.get(i))
    return lista

def pesquisa_probabilistica(dicionario_atualizado : dict):
    limparCampo(listbox)

    pesquisa = campoInputPalavra.get("1.0", "end-1c") 
    similaridade = []
    matriz_pesquisa = {}
    pesquisa = re.findall(r'\w+', pesquisa)

    for palavra in pesquisa:
        matriz_pesquisa[palavra] = 0
    for palavra in pesquisa:
        if(matriz_pesquisa[palavra]==0):
            matriz_pesquisa[palavra] = 1
    global matriz_pesquisa_global
    matriz_pesquisa_global = matriz_pesquisa

    similaridade = gerar_similaridade_simples(dicionario_atualizado, matriz_pesquisa)
    similaridade = sorted(similaridade, key=lambda item: item[1],reverse=True)

    for itens in similaridade:
        listbox.insert(END,itens)
    if (btnInserirArquivo['state'] != tk.NORMAL):
        btnInserirArquivo['state'] = tk.NORMAL
        
    return similaridade  

def executarFormatacaoDoArquivo(arquivos):
    a = 1
    for arquivo in arquivos:
        aux = {}
        with open(arquivo) as fp:
            soup = BeautifulSoup(fp, 'html.parser')
            textoSemFormatacao = BeautifulSoup(soup.text, 'html.parser').get_text()
            textohtml = []
            
            fp.close()
        #Separa todas as palavras uma a uma
        tokenizer = RegexpTokenizer(r'\w+')
        tokens = tokenizer.tokenize(textoSemFormatacao)
        texto_token = nltk.Text(tokens)

        #Retira os acentos do portugues
        stop = set(nltk.corpus.stopwords.words('portuguese'))
        texto_stop = (a for a in texto_token if a.lower() not in stop)

        #Remoção de toda pontuação, tal como () ou []...
        retirarPontuacao = re.compile('.[A-Za-z].')
        textoFormatado = (a for a in texto_stop if retirarPontuacao.match(a))

        #Acima foi removido todos os caracteres especiais do texto presente no html e armazenada todas as palavras em textoFormatado
        
        for palavra in textoFormatado:
            palavra = removerCaracteresEspeciais(palavra)
            textohtml.append(palavra.lower())
            arquivo = os.path.basename(arquivo)
            LISTA_DE_PALAVRAS.append(textohtml)
            textohtml.append(arquivo)
        aux.update(Counter(textohtml))
        DICIONARIO[a] = aux
        a += 1
    return DICIONARIO

def abrirArquivoHtml():
    #Abre os arquivos e armazena todo o texto do mesmo
    
    arquivos = filedialog.askopenfilenames(title="Escolha um Arquivo") 
    DICIONARIO = executarFormatacaoDoArquivo(arquivos)
    #Cria uma lista utilizando Quantidade como a variavél
    construirDicionario(DICIONARIO)
    dicionarioAtualizado = carregarDicionario()
    DICIONARIO = dicionarioAtualizado
    return dicionarioAtualizado



root=tk.Tk()
root.title("Contador de Palavras")

canvas = tk.Canvas(root,height=450, width=420, bg="#263D42")

frame = tk.Frame(root,bg="#263D42")
frame.place(relheight=1,relwidth=0.8,relx=0.1,rely=0.1)

btnSair = tk.Button(frame,text="Sair",padx=10,pady=5,fg="white",bg="#263D42",anchor="ne")

btnAdicionarArquivo = tk.Button(frame,text="Adicionar Arquivo", padx=7,pady=3,fg="white",bg="#263D42",anchor="ne")
btnAdicionarArquivo['command'] = command= lambda:abrirArquivoHtml()

campoInputPalavra = tk.Text(frame, height = 1, width = 20)

labelBool = tk.Label(frame,text="Digite a(s) palavra(s) e clique no botão para a pesquisar", bg="#263D42")


btnProcurarNosArquivos = tk.Button(frame,text="Procurar palavra(s)",padx=10,pady=3,fg="white",bg="#263D42")
btnProcurarNosArquivos['command'] = command= lambda:pesquisa_probabilistica(DICIONARIO)

btnInserirArquivo = tk.Button(frame,text="Adicionar Arquivo/s para pesquisa",padx=10,pady=3,fg="white",bg="#263D42",state=DISABLED)
btnInserirArquivo['command'] = command= lambda:gerar_similaridade_completa(DICIONARIO)

canvas.grid(column=0,row=0)

btnAdicionarArquivo.grid(column=1,row=1,pady=4)

labelBool.grid(column=1,row=2,pady=4)

campoInputPalavra.grid(column=1,row=3, padx=5)

btnProcurarNosArquivos.grid(column=1,row=5,pady=4)
btnInserirArquivo.grid(column=1,row=7,pady=4)

labelConfig = tk.Label(frame,text="", bg="#263D42")
labelConfig.grid(column=1,row=6,pady=4)

btnSair['command'] =root.quit
btnSair.grid(column=1,row=8)

listbox = tk.Listbox(frame, height = 10, width = 49,selectmode=MULTIPLE)
vertscroll = tk.Scrollbar(frame)
vertscroll.config(command=listbox.yview)


listbox.config(yscrollcommand = vertscroll.set)
listbox.grid(column=1,row=6)
vertscroll.grid(column=2,row=6,sticky='NS')

root.mainloop()