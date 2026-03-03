import redis

r = redis.Redis(
    host='redis-13499.c16.us-east-1-2.ec2.cloud.redislabs.com',
    port=13499,
    decode_responses=True,
    username="default",
    password="pMVGQJK4owGqrnZgPCdOOnJwafZbi83N",
)

r.publish("notificacoes", "Usuário atualizado com sucesso!")
print("✅ Mensagem enviada!")