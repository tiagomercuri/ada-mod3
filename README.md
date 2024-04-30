# Cluster Kubernets

## Como iniciar

- Vá até a pasta kubernets e execute o comando no bash abaixo:

```BASH
minikube start
```

- Depois que o minikube estiver ativo, execute os comandos para aplicar as configurações do kubernets que estão nos diretorios:

```BASH
kubectl apply -f volumes/
kubectl apply -f secrets/
kubectl apply -f configs/
kubectl apply -f services/
kubectl apply -f deployments/
```

- Certifique-se de que os PODs estão executando "running", e executando o comando:
```BASH
kubectl get pods
```

- Depois que os PODs estiverem executando normalmente, execute o comando abaixo para acessar o minio, lembre-se de colocar o nome do POD do minio que vai verificar no passo anterior, exemplo "minio-7598687489-hh5c8" e substituir no comando no trecho <nome-do-pod>:

```BASH
kubectl port-forward pod/<nome-do-pod> 8080:9000
```

- Entre no navegador e acesse: http://localhost:8080 e utilize o usuário e senha abaixo.

MINIO_USER: ROOTNAME 
MINIO_PASSWORD: CHANGEME123

- Depois, você precisa gerar um bucket e gerar o access key pela primeira vez no min.io pelo navegador (http://localhost:8080). Feito isso, vá na linha 13 e 14 do arquivo 'fraud-validator-consumer.py' e substitua os campos.

MINIO_ACCESS_KEY = "UHUVRLxqMUV2BUuD9ywB" 
MINIO_SECRET_KEY = "F4M8xU71sdj2JmkCZXTap9Tzrktm9WYwJRvTofqD"

====================================================================================