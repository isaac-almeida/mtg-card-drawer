import json
import os
import random
from bs4 import BeautifulSoup
import requests
import urllib.request
import shutil

nome_deck = 'sharktocrab & friends'


# cria um arquivo json com as informações do deck, a partir do .txt que o MTGA fornece
def jsonificar_deck(nome):
    with open(nome+'.txt', 'r',  encoding='utf-8') as file:
        tudo = file.readlines()

    cartas = {}
    # separando o nome da carta do número de cartas dessa que tem no deck
    for linha in tudo:
        pedacos = linha.split(' ')
        numero = int(pedacos[0])
        pedacos.pop()
        pedacos.pop()
        pedacos.pop(0)
        nome_carta = ' '.join(pedacos)
        # cartas de alquimia vem com um A- desnecessário na frente
        nome_carta = nome_carta.replace("A-", "")
        cartas.update({nome_carta: numero})

    with open(f'{nome}/{nome}.json', 'w',  encoding='utf-8') as file:
        file.write(json.dumps(cartas, ensure_ascii=False))


class ImgHandler:
    def download_img(self, pasta, carta, img_link, numero):
        caminho = f'./{pasta}/{numero} - {carta}.jpg'
        urllib.request.urlretrieve(img_link, caminho)
        return

    def get_img_link(self, card_name):
        url = 'https://mtg.cardsrealm.com/en-us/card/' + card_name
        req = requests.get(url)
        if req.status_code != 200:
            return ""
        soup = BeautifulSoup(req.text, 'html.parser')
        return soup.find(id="cardImage")["src"]


class CardHandler:
    def __init__(self, nome):
        # cria uma pasta com o nome do deck, caso já não exista
        if not os.path.exists(os.getcwd() + '/' + nome):
            os.mkdir(os.getcwd() + '/' + nome)
        self.nome = nome
        jsonificar_deck(nome)

        with open(f'{nome}/{nome}.json', 'r',  encoding='utf-8') as file:
            deck = json.loads(file.read())

        # salva na variável 'baralho', do objeto, uma lista com todas as cartas, simulando o próprio baralho
        self.baralho = []
        for carta in deck:
            for n in range(deck[carta]):
                self.baralho.append(carta)

    # embaralha as cartas salvas na lista 'baralho'
    def embaralhar(self):
        random.shuffle(self.baralho)
        return

    # faz o download e renomeia as imagens das cartas do deck, de acordo com a ordem presente em 'baralho'. Um exemplo de nome arquivo de carta: 14 - Forest. Indica que essa é a 14° carta que seria puxada do deck.
    def mostrar_cartas(self):
        fotografo = ImgHandler()
        # retorna um objeto em que as chaves são as cartas já baixadas na pasta desse deck, e os valores são uma lista contendo as posições que essas cartas estavam ocupando. Essa informação é usada depois pra renomear essas cartas, atribuindo uma nova posição a elas, já que o baralho fica sendo embaralhado o tempo todo.
        cartas_ja_existentes = self._buscar_imagens_localmente()
        n = 0
        for carta in self.baralho:
            if carta not in cartas_ja_existentes:
                # caso a imagem da carta já não esteja baixada, ele pesquisa pelo nome da carta, e baixa, e já renomeia a carta conforme a posição dela no baralho. Usa as duas funções do ImgHandler pra isso.
                link_imagem = fotografo.get_img_link(carta)
                if link_imagem:
                    fotografo.download_img(self.nome, carta, link_imagem, n)
            else:
                localizacao_cartas = f"{os.getcwd()}/{self.nome}"
                # o padrão para os valores do objeto 'cartas_ja_existentes' é uma lista contendo as posições antigas das cartas, porque ele é gerado pelo método _buscar_imagens_localmente. Porém, caso, numa nova leitura do deck, mais cartas de uma mesma forem encontradas, é preciso duplicar o arquivo até que se tenha um número igual de arquivos e cartas.
                if type(cartas_ja_existentes[carta]) == list:
                    numero_carta = cartas_ja_existentes[carta].pop()
                    try:
                        os.rename(
                            f"{localizacao_cartas}/{numero_carta} - {carta}.jpg",
                            f"{localizacao_cartas}/{n} - {carta}.jpg"
                        )
                    except:
                        pass
                    # quando a lista de posições de uma carta se esgota, substituímos a lista pela posição da última carta dessa que foi salva.
                    if not cartas_ja_existentes[carta]:
                        cartas_ja_existentes[carta] = n
                else:
                    # entra nessa condição somente se o tipo do valor encontrado em cartas_ja_existentes[carta] não for uma lista, isto é, caso tenha passado pelo código logo acima, e o vetor tenha se esgotado. Nesse caso, o arquivo é duplicado, e o novo recebe o número adequado no começo do nome:
                    shutil.copy(
                        f"{localizacao_cartas}/{cartas_ja_existentes[carta]} - {carta}.jpg",
                        f"{localizacao_cartas}/{n} - {carta}.jpg"
                    )

            n += 1

    def _buscar_imagens_localmente(self):
        tudo = os.listdir(f"{os.getcwd()}/{self.nome}")
        tudo.pop(tudo.index(self.nome + '.json'))

        imagens = {}
        for nome_arquivo in tudo:
            nome_sem_extensao = nome_arquivo.replace('.jpg', '')
            pedacos = nome_sem_extensao.split(" ")
            numero = pedacos.pop(0)
            pedacos.pop(0)
            carta = ' '.join(pedacos)
            imagens.update({
                carta: [*imagens.get(carta, []), numero]
            })
        return imagens


deck = CardHandler(nome_deck)
deck.embaralhar()
for carta in deck.baralho:
    print(carta)
deck.mostrar_cartas()
