class Tweet:
    def __init__(self, nome, texto, data_post, cidade, id_ref):
        self.nome = nome 
        self.texto = texto
        self.data_post = data_post
        self.palavra_chave = None
        self.is_palavrao = None
        self.sentiment = None
        self.cidade = cidade
        self.id_ref = id_ref