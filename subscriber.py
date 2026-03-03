import redis

r = redis.Redis(
    host='redis-13499.c16.us-east-1-2.ec2.cloud.redislabs.com',
    port=13499,
    decode_responses=True,
    username="default",
    password="pMVGQJK4owGqrnZgPCdOOnJwafZbi83N",
)

pubsub = r.pubsub()
pubsub.subscribe("notificacoes")

print("🔔 Aguardando mensagens...")

for mensagem in pubsub.listen():
    if mensagem["type"] == "message":
        print("📩 Recebido:", mensagem["data"])