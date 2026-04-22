import cv2 # Biblioteca para visão computacional
from pyzbar.pyzbar import decode # Biblioteca que identifica o código de barras

# 1. Nosso "Banco de Dados" de exemplo
mercado_db = {
    "7891234567890": {"nome": "Arroz 5kg", "preco": 25.50},
    "7899876543210": {"nome": "Feijão 1kg", "preco": 8.90},
    "7895554443332": {"nome": "Leite Integral", "preco": 4.50}
}

carrinho = []
total = 0.0

def adicionar_ao_carrinho(codigo):
    global total
    if codigo in mercado_db:
        produto = mercado_db[codigo]
        carrinho.append(produto)
        total += produto['preco']
        print(f"Adicionado: {produto['nome']} - R$ {produto['preco']:.2f}")
        print(f"Total Atual: R$ {total:.2f}")
    else:
        print("Produto não cadastrado!")

# 2. Lógica para abrir a câmera e ler
def iniciar_scanner():
    cap = cv2.VideoCapture(0) # Abre a câmera do celular/pc
    print("Aproxime o código de barras da câmera... (Pressione 'q' para sair)")

    while True:
        _, frame = cap.read()
        codigos = decode(frame) # Tenta encontrar um código na imagem

        for obj in codigos:
            codigo_lido = obj.data.decode('utf-8')
            adicionar_ao_carrinho(codigo_lido)
            cv2.waitKey(2000) # Espera 2 segundos para não ler o mesmo item mil vezes

        cv2.imshow("Scanner de Compras", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Rodar o scanner
iniciar_scanner()
