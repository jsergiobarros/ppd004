#import json
import socket
import time

from common import pack, unpack


class Client():
    def __init__(self, addr: tuple):
        self.__socket = socket.socket()
        self.__socket.connect(addr)

    def close(self):
        self.__socket.close()

    # Este metodo casta a mensagem recebida para o tipo especificado
    @staticmethod
    def __cast(cast_type, message):
        if cast_type is str:
            return message
        if cast_type is int:
            return int(message)
        if cast_type is float:
            return float(message)

    # este metodo recebe as mensagens, note que ele também da split no ':', vide o formato da mensagem
    def __receiveAll(self):
        buffer = b''
        size = -1

        while True:
            data = self.__socket.recv(1024)

            if len(data.split(b':', 1)) == 2: # tentando obter o tamanho
                size, data = data.split(b':', 1)
                size = int(size)
            else:
                buffer += data
                data = b''

            if size > 0 and len(data) >= size: # ja leu o que queria
                buffer = data

                return buffer

    # este metodo compacta a mensagem do tipo push e envia ao servidor
    def _out(self, data: tuple):
        message = pack({'operation': 'push', 'author': data[0], 'topic': data[1], 'message': data[2]})
        self.__socket.send(message) # envia uma açao de push

    def _outtm(self, data: tuple):
        message = pack({'operation': 'push', 'author': data[0], 'topic': data[1], 'message': data[2]})
        self.__socket.send(message) # envia uma açao de push
        time.sleep(int(data[3]))
        self._in((data[0],data[1],data[2],data[3]))

    # este metodo compacta a mensagem do tipo peek, envia ao servidor e entao espera uma resposta
    def _rd(self, data: tuple):
        message = pack({'operation': 'peek', 'author': data[0], 'topic': data[1]})
        self.__socket.send(message) # faz o request pela leitura

        responseStr = self.__receiveAll().decode('utf-8') # espera pela resposta
        response = unpack(responseStr)

        return self.__cast(data[2], response['message'])

    # este metodo compacta a mensagem do tipo in, envia ao servidor, recebe uma resposta e casta o resultado par ao tipo recebido pelo parametro data[2]
    def _in(self, data: tuple):
        message = pack({'operation': 'pop', 'author': data[0], 'topic': data[1]})
        self.__socket.send(message) # faz o request pela leitura e remoção

        response = unpack(self.__receiveAll().decode('utf-8'))

        return self.__cast(data[2], response['message'])
