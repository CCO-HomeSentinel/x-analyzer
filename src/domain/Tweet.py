class Tweet:
    def __init__(self, nome, texto, data_post, residencia_id, id_ref):
        self.nome = nome 
        self.texto = texto
        self.data_post = data_post
        self.palavra_chave = None
        self.is_palavrao = None
        self.residencia_id = residencia_id
        self.sentiment = None
        self.id_ref = id_ref