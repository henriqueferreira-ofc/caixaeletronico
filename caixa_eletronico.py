import hashlib
from datetime import datetime
import hashlib
import time
import json
import random
from getpass import getpass
# Usuários e seus dados
usuarios = {
    "admin": {
        "senha": hashlib.sha256("admin123".encode()).hexdigest(),
        "tipo": "admin",
    },
    "cliente1": {
        "senha": hashlib.sha256("cliente123".encode()).hexdigest(),
        "tipo": "cliente",
        "saldo": 1000.0,
        "historico": [],
        "limite_saque": 500.0,
        "limite_transferencia": 1000.0,
        "notificacoes": True,
        "bloqueado": False,
        "tentativas": 0,
    },
    "cliente2": {
        "senha": hashlib.sha256("cliente456".encode()).hexdigest(),
        "tipo": "cliente",
        "saldo": 1500.0,
        "historico": [],
        "limite_saque": 700.0,
        "limite_transferencia": 2000.0,
        "notificacoes": True,
        "bloqueado": False,
        "tentativas": 0,
    }
}

# Log global do sistema
log_global = []

# Função para registrar logs
def registrar_log(acao):
    horario = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_global.append(f"{horario} - {acao}")

# Função de notificações para usuários
def enviar_notificacao(usuario, mensagem):
    if usuarios[usuario].get("notificacoes", False):
        print(f"\n🔔 Notificação para {usuario}: {mensagem}")

# Menu do administrador
def menu_admin():
    while True:
        print("\n=== Menu do Administrador ===")
        print("1. Verificar saldo total no sistema")
        print("2. Gerar relatórios")
        print("3. Gerenciar limites de usuários")
        print("4. Exibir logs do sistema")
        print("5. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            saldo_total = sum([dados["saldo"] for login, dados in usuarios.items() if dados.get("saldo") is not None])
            print(f"Saldo total no sistema: R$ {saldo_total:.2f}")

        elif opcao == "2":
            gerar_relatorios()

        elif opcao == "3":
            gerenciar_limites()

        elif opcao == "4":
            exibir_logs()

        elif opcao == "5":
            break

        else:
            print("❌ Opção inválida. Tente novamente.")

# Menu do cliente
def menu_cliente(usuario_logado):
    while True:
        print("\n=== Menu do Cliente ===")
        print("1. Consultar saldo")
        print("2. Realizar saque")
        print("3. Realizar transferência")
        print("4. Ver histórico de transações")
        print("5. Configurar notificações")
        print("6. Visualizar limites")
        print("7. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            print(f"Seu saldo é: R$ {usuarios[usuario_logado]['saldo']:.2f}")

        elif opcao == "2":
            realizar_saque(usuario_logado)

        elif opcao == "3":
            realizar_transferencia(usuario_logado)

        elif opcao == "4":
            historico = usuarios[usuario_logado]["historico"]
            if historico:
                print("\n=== Histórico de Transações ===")
                for transacao in historico:
                    print(transacao)
            else:
                print("Nenhuma transação encontrada.")

        elif opcao == "5":
            configurar_notificacoes(usuario_logado)

        elif opcao == "6":
            visualizar_limites(usuario_logado)

        elif opcao == "7":
            break

        else:
            print("❌ Opção inválida. Tente novamente.")

# Função para login
def login():
    while True:
        print("\n=== Tela de Login ===")
        login = input("Digite seu login: ")

        if login in usuarios:
            if usuarios[login]["bloqueado"]:
                print("❌ Esta conta está bloqueada. Contate o administrador.")
                continue

            senha = input("Digite sua senha: ")
            senha_hash = hashlib.sha256(senha.encode()).hexdigest()

            if senha_hash == usuarios[login]["senha"]:
                print("✅ Login realizado com sucesso!")
                usuarios[login]["tentativas"] = 0  # Resetar tentativas em caso de sucesso
                return login

            else:
                print("❌ Senha incorreta.")
                usuarios[login]["tentativas"] += 1
                if usuarios[login]["tentativas"] >= 3:
                    usuarios[login]["bloqueado"] = True
                    print("❌ Conta bloqueada devido a tentativas de login inválidas.")
        else:
            print("❌ Usuário não encontrado.")

# Função para saque
def realizar_saque(usuario_logado):
    try:
        valor_saque = float(input("Digite o valor do saque: R$ "))
        if valor_saque <= 0:
            print("❌ Valor inválido.")
        elif valor_saque > usuarios[usuario_logado]["saldo"]:
            print("❌ Saldo insuficiente.")
        elif valor_saque > usuarios[usuario_logado]["limite_saque"]:
            print("❌ Valor excede o limite diário de saque.")
        else:
            usuarios[usuario_logado]["saldo"] -= valor_saque
            usuarios[usuario_logado]["historico"].append(f"Saque de R$ {valor_saque:.2f}")
            enviar_notificacao(usuario_logado, f"Você realizou um saque de R$ {valor_saque:.2f}.")
            registrar_log(f"{usuario_logado} realizou um saque de R$ {valor_saque:.2f}.")
            print(f"Saque realizado com sucesso. Seu saldo atual é: R$ {usuarios[usuario_logado]['saldo']:.2f}")
    except ValueError:
        print("❌ Entrada inválida.")

# Função para transferência
def realizar_transferencia(usuario_logado):
    destino = input("Digite o login do destinatário: ")
    if destino in usuarios and usuarios[destino]["tipo"] == "cliente":
        try:
            valor = float(input("Digite o valor da transferência: R$ "))
            if valor <= 0:
                print("❌ Valor inválido.")
            elif valor > usuarios[usuario_logado]["saldo"]:
                print("❌ Saldo insuficiente.")
            elif valor > usuarios[usuario_logado]["limite_transferencia"]:
                print("❌ Valor excede o limite diário de transferência.")
            else:
                usuarios[usuario_logado]["saldo"] -= valor
                usuarios[destino]["saldo"] += valor
                usuarios[usuario_logado]["historico"].append(f"Transferência de R$ {valor:.2f} para {destino}")
                usuarios[destino]["historico"].append(f"Transferência de R$ {valor:.2f} recebida de {usuario_logado}")
                enviar_notificacao(usuario_logado, f"Você transferiu R$ {valor:.2f} para {destino}.")
                enviar_notificacao(destino, f"Você recebeu uma transferência de R$ {valor:.2f} de {usuario_logado}.")
                registrar_log(f"{usuario_logado} transferiu R$ {valor:.2f} para {destino}.")
                print(f"Transferência realizada com sucesso. Seu saldo atual é: R$ {usuarios[usuario_logado]['saldo']:.2f}")
        except ValueError:
            print("❌ Entrada inválida.")
    else:
        print("❌ Destinatário não encontrado.")

# Sistema principal
def sistema_caixa():
    usuario = login()
    if usuario:
        if usuarios[usuario]["tipo"] == "admin":
            menu_admin()
        elif usuarios[usuario]["tipo"] == "cliente":
            menu_cliente(usuario)

# Iniciar o sistema
sistema_caixa()
#Henrique César Autor