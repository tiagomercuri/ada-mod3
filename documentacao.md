### Documentação do Sistema Kubernetes da Aplicação Financeira

## Arquitetura do Sistema
O sistema é composto pelos seguintes componentes principais:

1. Transaction Producer:
    Aplicação Python que publica mensagens de transações em uma fila RabbitMQ.
2. Fraud Validator Consumer:
    Aplicação Python que consome mensagens da fila RabbitMQ, realiza validação de fraude e armazena relatórios em um bucket MinIO.
3. MinIO:
    Armazena os relatórios gerados pela aplicação de validação de fraude (consumer).
4. RabbitMQ:
    Servidor de mensageria usado para intermediação das mensagens entre o "producer" e o "consumer" de transações.
5. Redis:
    Banco de dados em memória caching e armazenamento temporário durante a validação de transações.
    Gerido por um Deployment com um serviço ClusterIP para comunicações internas.

## Configuração e Lançamento

# ConfigMaps e Secrets

    ConfigMaps são usados para manter configurações não sensíveis que podem ser injetadas nos containers:
        app-config: Contém endereço e nome de buckets do MinIO.
        rabbitmq-config: Contém o host e a porta para acesso ao RabbitMQ.
        redis-config: Armazena a porta e o host do Redis.
    Secrets:
        minio-secret: Armazena credenciais de acesso ao MinIO.
        rabbitmq-secret: Contém credenciais de acesso ao RabbitMQ.

## Deployments e Demais Pastas


1. Deployments:
    Cria os Deployments para transaction-producer, fraud-validator-consumer, no arquivo app-deployments.yaml. O MinIO, RabbitMQ e Redis estão nos arquivos separados oara cada um. São as declarações, por exemplo de quantas replicas vão ter. No Cluster foi feito com 1 replica.
2. Services:
    Expõe cada componente, configurando ClusterIP, protocolo, portas. Aqui definimos como são acessados os componentes.
3. Volumes - Persistent Volumes e Claims (PV e PVC):
    Configura PersistentVolumes e PersistentVolumeClaims para garantir a persistência de dados para MinIO e Redis. São os Volumes que armazenam dados persistentes que os containers precisam acessar.



## Escalando os Serviços
Utiliza HorizontalPodAutoscalers (HPA) para escalar automaticamente os componentes baseando-se na utilização de CPU. Parâmetros minReplicas e maxReplicas podem ser ajustados conforme a demanda.


### Considerações da aplicação

O Relatório vai ser gerado em TXT após 15 segundos contados a partir da ultima mensagem. A regra de negócio foi definida: Uma transação é considerada fraudulenta se ocorrerem transações em estados diferentes em um curto período de tempo, indicando que não seria fisicamente possível para o cliente viajar entre esses locais tão rapidamente. Os estados são representados por número no relatorio. Se duas transações consecutivas para a mesma conta bancária ocorrem em estados diferentes com menos de 10 minutos de diferença entre elas, é fraude.