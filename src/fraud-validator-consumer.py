import json
import pika
import threading
import redis
from datetime import datetime, timedelta
from minio import Minio
from minio.error import S3Error
import os
import time

# Definindo variáveis de ambiente
MINIO_HOST = os.getenv('MINIO_HOST', 'minio-console-service.default.svc.cluster.local')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', '5iad6qo5aTpHA4hMxqrN')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'aJj6BrcQ9i0mF7tFyExWShyGdTyI8A80hXFhtdzo')
MINIO_BUCKET = os.getenv('MINIO_BUCKET', 'relatorio')
REDIS_HOST = os.getenv('REDIS_HOST', 'redis.relatorio.svc.cluster.local')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq-service.default.svc.cluster.local')
RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', '5672'))

# Inicializações
minio_client = Minio(f"{MINIO_HOST}:9000",
                     access_key=MINIO_ACCESS_KEY,
                     secret_key=MINIO_SECRET_KEY,
                     secure=False)
redis_conn = redis.Redis(host=REDIS_HOST, port=int(REDIS_PORT), db=0)
transacoes = []

# Temporizador para a geração automática do relatório
temporizador = None

def gerar_e_enviar_relatorio():
    global transacoes
    if not transacoes:
        print("Nenhuma transação recebida para gerar relatório.")
        return

    print("Iniciando a geração do relatório...")
    relatorio_content = "\n".join(
        [f"Transacao ID: {t['id']}, Conta: {t['account_number']}, Estado: {t['estado']}, Valor: {t['value']}, Data: {t['data']}" 
         for t in transacoes])
    relatorio_content += "\nExistem transações suspeitas." if any(t.get('suspeita', False) for t in transacoes) else "\nNão existem transações suspeitas."
    
    arquivo_relatorio = "relatorio_transacoes.txt"
    with open(arquivo_relatorio, 'w') as f:
        f.write(relatorio_content)
    
    try:
        minio_client.fput_object(MINIO_BUCKET, arquivo_relatorio, arquivo_relatorio)
        url = minio_client.presigned_get_object(MINIO_BUCKET, arquivo_relatorio, expires=timedelta(days=1))
        print(f"Relatório enviado para o MinIO com sucesso. URL: {url}")
    except S3Error as e:
        print(f"Erro ao enviar o relatório para o MinIO: {e}")

    transacoes.clear()

def iniciar_temporizador():
    global temporizador
    if temporizador is not None:
        temporizador.cancel()
    temporizador = threading.Timer(15.0, gerar_e_enviar_relatorio)
    temporizador.start()

def processar_transacao(channel, method, properties, body):
    global transacoes
    transacao = json.loads(body)
    print(f"Transação recebida: {transacao}")
    transacoes.append(transacao)
    iniciar_temporizador()

def main():
    connection = None
    channel = None
    while not connection:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, port=int(RABBITMQ_PORT), virtual_host="/"))
            channel = connection.channel()
        except pika.exceptions.AMQPConnectionError:
            print("Aguardando RabbitMQ estar disponível...")
            time.sleep(10)
        except Exception as e:
            print(f"Erro ao conectar com RabbitMQ: {e}")
            time.sleep(10)
    
    queue_name = "fraud_validator_queue"
    channel.queue_declare(queue=queue_name)
    channel.queue_bind(exchange='amq.fanout', queue=queue_name)
    channel.basic_consume(queue=queue_name, on_message_callback=processar_transacao, auto_ack=True)
    print("Esperando por mensagens. Para sair pressione CTRL+C")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Processo interrompido pelo usuário.")
    finally:
        if connection and connection.is_open:
            connection.close()

if __name__ == "__main__":
    main()
