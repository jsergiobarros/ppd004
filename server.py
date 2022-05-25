import asyncio

from collections import deque

from common import unpack, pack

tuple_space = {

}


class Server(asyncio.Protocol):
    def connection_made(self, transport: asyncio.Transport):
        self.__transport = transport
        self.__buffer = bytes()
        self.__tamanho_esperado = -1

    def connection_lost(self, exc: Exception):
        if exc is None:
            print('Aparentemente deu tudo certo')
        else:
            print('Deu errado: ', exc)

    # Retorna ou cria o tuple_space
    @staticmethod
    def __get_topic(author: bytes, topic: bytes):
        author_struct = tuple_space.get(author)
        if author_struct is None:
            author_struct = tuple_space[author] = {}

        topic_struct = author_struct.get(topic)
        if topic_struct is None:
            topic_struct = author_struct[topic] = {
                'msg_queue': deque(),
                'subscribed': deque()
            }

        return topic_struct

    # Este metodo itera pelos pedidos de subscribed e envia as mensagens aos usuarios corretos
    @staticmethod
    def __iterate_waiting(topic_struct: dict):
        msg_queue = topic_struct['msg_queue']
        subscribed = topic_struct['subscribed']
        while len(msg_queue) > 0 and len(subscribed) > 0: # para casa elemento que possui pelo menos um client inscrito
            message, conn = subscribed.popleft()
            message["message"] = msg_queue[0]
            conn.write(pack(message)) # envia a mensagem
            if message["operation"] == 'pop': # caso seja um pop/in, então remove o primeiro elemento da queue
                msg_queue.popleft()

    # Este metodo faz uma especie de subscribe
    def __register_conn(self, topic_struct: dict, message: dict):
        topic_struct['subscribed'].append((message, self.__transport))

    # Metodo chamado caso a operacao seja de push, ele adiciona à msg_queue e chama a iteracao
    def __push_op(self, message: dict):
        author = message['author']
        topic = message['topic']
        data = message['message']

        topic_struct = self.__get_topic(author, topic)
        topic_struct['msg_queue'].append(data) # coloca a mensagem na fila
        self.__iterate_waiting(topic_struct) # itera na fila, enviando a nova mensagem para alguem que queira recebe-la

    # Metodo chamado caso a operacao seja de peek, ele adiciona o usuario em uma lista de espera e chama a iteracao
    def __peek_op(self, message: dict):
        author = message['author']
        topic = message['topic']

        topic_struct = self.__get_topic(author, topic)

        self.__register_conn(topic_struct, message)
        self.__iterate_waiting(topic_struct) # itera na lista, enviando a resposta

    # Metodo chamado caso a operacao seja de pop, ele adiciona o usuario em uma lista de espera e chama a iteracao
    def __pop_op(self, message: dict):
        author = message['author']
        topic = message['topic']

        topic_struct = self.__get_topic(author, topic)
        self.__register_conn(topic_struct, message) # adiciona o client na fila, indicando que ele quer receber alguma mensagem
        self.__iterate_waiting(topic_struct) # itera na lista, enviando a resposta

    # Esse metodo desvia o request para seu endpoint correto
    def __parse(self, dataStruct: dict):
        if dataStruct['operation'] == 'push':
            self.__push_op(dataStruct)
        elif dataStruct['operation'] == 'peek':
            self.__peek_op(dataStruct)
        elif dataStruct['operation'] == 'pop':
            self.__pop_op(dataStruct)

    # Esse metodo recebe dados, o formato da mensagem é numero_de_caracteres:json_do_request, por isso realizamos um split
    def data_received(self, data: bytes):
        while len(data) > 0:
            if self.__tamanho_esperado < 0:

                if len(data.split(b':', 1)) == 2: # obtendo o tamanho esperado
                    size, data = data.split(b':', 1)
                    try:
                        self.__tamanho_esperado = int(size)
                    except ValueError:
                        self.__transport.close()

            self.__buffer = data[:self.__tamanho_esperado]

            if self.__tamanho_esperado > 0 and len(data) >= self.__tamanho_esperado: # ja leu tudo que deveria
                data = data[self.__tamanho_esperado:]
                self.__tamanho_esperado = -1
                self.__parse(unpack(self.__buffer.decode('utf-8'))) # da unpack e então parse
                self.__buffer = bytes()

    # Define o servidor assincrono
    @classmethod
    async def __main(cls, host: str, port: int):
        loop = asyncio.get_event_loop()
        server = await loop.create_server(lambda: cls(), host, port)

        async with server:
            await server.serve_forever()

    @classmethod
    def start_server(cls, host='127.0.0.1', port=5050):
        print(host)
        asyncio.run(cls.__main(host, port))
