import random
import socket
import threading
import time
from tkinter import *
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from client import Client
from server import Server
from functools import partial
NOME = ""
DIRETO=""
TOPICO = ""
USERS=[]
USR=[]
CANAIS=[]
CLIENTE=0
topicovigente=0
ip_local = socket.gethostbyname(socket.gethostname())
control=0
BOOL=TRUE

def main_chat():
    global CANAIS,CLIENTE,USERS,TOPICO,NOME
    def criacanal():
        nome = cria_canal.get()
        try:
            CANAIS.index(nome)
            messagebox.showwarning(title="Nome ja cadastrado",message="Nome ja cadastrado, tente outro")
            cria_canal.delete(0,END)
            return
        except:
            pass
        cria_canal.delete(0,END)
        aux=CLIENTE._in(('shared', 'canal', str))
        aux= aux+':'+nome
        CLIENTE._out(('shared', 'canal', aux))
        CLIENTE._out(('user', nome, "VAZIO"))


    janela = Tk()
    janela.geometry(("800x600"))




    janela.resizable(False, False)
    endereco = Entry(janela,width=75)
    endereco.insert(0,"Chat no endereço: "+ip_local+" - Nome: "+NOME)
    endereco["state"]='disabled'
    endereco.place(x=10,y=10)

    cria_canal = Entry(janela,width=10)
    cria_canal.place(x=470,y=10)

    botao_cria=Button(janela,text="Criar Canal",command=criacanal)
    botao_cria.place(x=540,y=10)



    topicos = Canvas(janela, bg='white', width=250, height=200)
    #botoes para os topicos

    def muda_canal(topic,button):
        global TOPICO,topicovigente
        CLIENTE2 = Client((ip_local, 5050))
        if TOPICO==topic:
            return
        if topicovigente!=0:
            topicovigente["bg"] = "#d3d3d3"
            topicovigente["fg"] = "black"
        nomes_temp=CLIENTE2._rd(('user', topic, str))
        try:
            nomes_temp.index(NOME)
            messagebox.showwarning(title="ja existe um usuario com esse nome nesse canal",message="Ja existe um usuario com esse nome nesse canal\nTente outro")
            return
        except:
            pass
        CLIENTE2._out((TOPICO, "mensagem publica", NOME+" mudou"))
        CLIENTE2._out((TOPICO, NOME, "mudou"))
        srt("")
        aux = CLIENTE2._in(('user', TOPICO, str))
        aux = aux.split(":")
        aux.remove(NOME)
        aux = ":".join(aux)
        if (aux==""):
            CLIENTE2._out(('user', TOPICO, "VAZIO"))
        else:
            CLIENTE2._out(('user', TOPICO, aux))
        CLIENTE2.close()
        TOPICO=topic
        for i in USR:
            i.destroy()
        button["bg"]="black"
        button["fg"] = "white"
        topicovigente=button
        get_users()

    def srt(text):
        global DIRETO
        DIRETO=text
        lbl_direto["text"]=DIRETO


    def get_users():
        global USERS,USR,ip_local,TOPICO,NOME
        CLIENTE2 = Client((ip_local, 5050))
        aux2 = CLIENTE._in(('user', TOPICO, str))
        if aux2 == 'VAZIO':
            CLIENTE2._out(('user', TOPICO, NOME))
            user = Button(users, text=NOME,state=DISABLED)
            USERS.append(NOME)
            USR.insert(0, user)
            user.grid(row=0)
            return
        CLIENTE2._out(('user', TOPICO, aux2 + ":" + NOME))
        aux2=NOME+":"+aux2
        USERS=aux2.split(":")
        CLIENTE2.close()
        atualizanome()


    def atualizanome():
        global USR,USERS
        CLIENTE2 = Client((ip_local, 5050))
        aux = CLIENTE2._rd(('user', TOPICO, str))
        USERS = aux.split(":")
        for i in USR:
            i.destroy()
        USR = []
        for x in range(len(USERS)):
            user = Button(users, text=USERS[x])
            user["command"]=partial(srt,USERS[x])
            if(USERS[x]==NOME):
                user["state"]=DISABLED
            USR.insert(x,user)
            user.grid(row=x)
        CLIENTE2.close()


    def inclui_canais(inicio):
        for x in range(inicio,len(CANAIS)):
            topic = Button(topicos,text=CANAIS[x],bg='#d3d3d3')
            topic["command"]=partial(muda_canal,CANAIS[x],topic)
            topic.grid(padx=5,row=0,column=x)


    inclui_canais(0)
    topicos.place(x=10,y=40)
    users = Canvas(janela, width=100, height=500)
    users.place(x=650,y=70)
    #botoes para os topicos

    def insert_public():  ###metodo de INSERIR MENSAGEM
        texto=entry_group.get()
        CLIENTE._out((TOPICO,"mensagem publica",NOME+": "+TOPICO+": "+texto))
        entry_group.delete(0,END)
        CLIENTE._in((TOPICO, "mensagem publica", str))

    def insert_private():  ###metodo de INSERIR MENSAGEM
        try:
            USERS.index(DIRETO)
        except:
            messagebox.showwarning(title="Usuario não cadastrado",message="Nenhum Usuario selecionado ou cadastrado")
            entry_private.delete(0, END)
            srt("")
            return
        texto=entry_private.get()
        CLIENTE._out((TOPICO, DIRETO, NOME + ": " + TOPICO + ": " + texto))
        chat_private.configure(state='normal')
        chat_private.insert(END, NOME+": "+TOPICO+": "+texto)
        chat_private.insert(END, "\n")
        chat_private.see('end')
        chat_private.configure(state='disabled')
        entry_private.delete(0,END)
        CLIENTE._in((TOPICO, DIRETO, str))

    chat_public = ScrolledText(janela, width=75, height=10, state='disabled')
    chat_public.place(x=10, y=70)
    entry_group = Entry(janela, width=75)
    entry_group.place(x=10,y=245)
    send_group = Button(janela, text="Enviar Grupo", command=insert_public)
    send_group.place(x=475, y=245)

    lbl_direto=Label(janela, width=20, text=DIRETO)
    lbl_direto.place(x=10, y=270)

    chat_private = ScrolledText(janela, width=75, height=10, state='disabled')
    chat_private.place(x=10, y=300)
    entry_private = Entry(janela, width=75)
    entry_private.place(x=10, y=475)
    send_private = Button(janela, text="Enviar Privado", command=insert_private)
    send_private.place(x=475, y=475)


    def msg_publica():
        global BOOL
        CLIENTE2 = Client((ip_local, 5050))
        while BOOL:
            mensagem_publica=CLIENTE2._rd((TOPICO,"mensagem publica", str))
            if(mensagem_publica==NOME+" mudou"):
                CLIENTE2._in((TOPICO,"mensagem publica", str))
                time.sleep(2)
            else:
                chat_public.configure(state='normal')
                chat_public.insert(END, mensagem_publica)
                chat_public.insert(END, "\n")
                chat_public.see('end')
                chat_public.configure(state='disabled')


    def msg_particular():
        global BOOL
        CLIENTE2 = Client((ip_local, 5050))
        while BOOL:
            mensagem_particular=CLIENTE2._rd((TOPICO,NOME, str))
            if(mensagem_particular=="mudou"):
                CLIENTE2._in((TOPICO,NOME, str))
                time.sleep(2)
            else:
                chat_private.configure(state='normal')
                chat_private.insert(END, mensagem_particular)
                chat_private.insert(END, "\n")
                chat_private.see('end')
                chat_private.configure(state='disabled')


    def canais():
        global CANAIS
        while BOOL:
            time.sleep(2)
            atualizanome()
            aux=CLIENTE._rd(('shared', 'canal', str)).split(":")
            if len(aux)>len(CANAIS):
                inicio =len(CANAIS)
                CANAIS= aux
                inclui_canais(inicio)


    privado = threading.Thread(target=msg_particular)
    privado.start()
    publico = threading.Thread(target=msg_publica)
    publico.start()
    canal=threading.Thread(target=canais)
    canal.start()

    def desliga():
        global BOOL,CLIENTE,TOPICO
        BOOL=False
        aux = CLIENTE._in(('user', TOPICO, str))
        aux = aux.split(":")
        aux.remove(NOME)
        aux = ":".join(aux)
        if (aux == ""):
            CLIENTE._out(('user', TOPICO, "VAZIO"))
        else:
            CLIENTE._out(('user', TOPICO, aux))


        janela.destroy()
    janela.protocol("WM_DELETE_WINDOW", desliga)
    janela.mainloop()



def define_nome():

    def iniciar():
        global NOME, CLIENTE,USERS,CANAIS,TOPICO,ip_local
        NOME=nome.get()
        try:
            CLIENTE=Client((endereco.get(), 5050))
            ip_local=endereco.get()
            aux=CLIENTE._in(('user', 'publico', str))


            if(aux=="VAZIO"):
                CLIENTE._out(('user', 'publico', NOME))
                USERS.append(NOME)
            else:
                CLIENTE._out(('user', 'publico', aux + ':' + NOME))
                aux = NOME + ":" + aux
                USERS = aux.split(":")
            TOPICO = 'publico'
            CANAIS=CLIENTE._rd(('shared', 'canal', str)).split(":")

        except:
            if(messagebox.askyesno(title="Servidor não existe", message=f"Servidor não existe, deseja iniciar um no ip{ip_local}?")):
                server = threading.Thread(target=lambda: Server.start_server(host=ip_local))
                server.start()
                CLIENTE = Client((endereco.get(), 5050))
                CLIENTE._out(('user', 'publico', NOME))
                CLIENTE._out(('user', 'todos', "VAZIO"))
                CLIENTE._out(('user', 'auxiliar', "VAZIO"))
                TOPICO='publico'
                CLIENTE._out(('shared', 'canal', 'publico:todos:auxiliar'))
                CANAIS='publico:todos:auxiliar'.split(":")

            else:
                return

        janela.destroy()
        main_chat()

    janela = Tk()
    janela.geometry(("150x150"))
    endereco=Entry(janela,width=20)
    nome=Entry(janela,width=20)
    iniciar = Button(janela,text="Inicar Chat",command=iniciar)



    endereco.insert(0,ip_local)
    aux = "Usuário" + str(random.randint(10000, 100000))
    nome.insert(0,aux)
    nome.grid(pady=10,padx=10,row=0)
    endereco.grid(pady=10,padx=10,row=1)
    iniciar.grid(pady=10,padx=10,row=2)
    janela.mainloop()


define_nome()


