import datetime
import pika
import json
import time
import random

def conectar_a_rabbitmq():
    connection = None
    while not connection:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq", port=5672, virtual_host="/"))
            channel = connection.channel()
            print("Conexão com RabbitMQ estabelecida.")
            return connection, channel
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Aguardando RabbitMQ estar disponível... {str(e)}")
            time.sleep(10)  # Espera 10 segundos antes de tentar novamente
        except Exception as e:
            print(f"Erro ao conectar com RabbitMQ: {str(e)}")
            time.sleep(10)

def publicar_mensagens(channel, transactions):
    properties = pika.BasicProperties(app_id="transaction-producer.py", content_type="application/json")
    print("Iniciando publicação de mensagens...")
    for transaction in transactions:
        transaction["account_number"] = random.randint(1, 10000)
        transaction["estado"] = random.randint(1, 27)
        transaction["data"] = datetime.datetime.utcnow().isoformat() + 'Z'

        channel.basic_publish(
            exchange="amq.fanout",
            routing_key="",
            body=json.dumps(transaction),
            properties=properties,
        )
        print(f"[x] Sent '{json.dumps(transaction)}'")
        time.sleep(5)

def carregar_transacoes_do_arquivo(nome_do_arquivo):
    with open(nome_do_arquivo) as transaction_file:
        transactions = json.load(transaction_file)
    return transactions

def main():
    connection, channel = conectar_a_rabbitmq()
    transactions = carregar_transacoes_do_arquivo("transaction.json")
    if transactions:
        publicar_mensagens(channel, transactions)
    else:
        print("Nenhuma transação para enviar.")
    channel.close()
    connection.close()
    while True:
        print("Mantendo o serviço ativo...")
        time.sleep(60)

if __name__ == "__main__":
    main()
