class Fila:
    def __init__(self):
        self._itens = []

    def enqueue(self, item) -> None:
        self._itens.append(item)

    def inserir_em(self, posicao: int, item) -> None:
        self._itens.insert(posicao, item)

    def vazia(self) -> bool:
        return len(self._itens) == 0

    def tamanho(self) -> int:
        return len(self._itens)

    def listar(self) -> list:
        return list(self._itens)

    def dequeue(self):
        if self.vazia():
            return None
        return self._itens.pop(0)

    def remover_por_id(self, cliente_id: int) -> None:
        self._itens = [item for item in self._itens if item["id"] != cliente_id]
