"""Basic connection example.
"""

import redis

r = redis.Redis(
    host='redis-13499.c16.us-east-1-2.ec2.cloud.redislabs.com',
    port=13499,
    decode_responses=True,
    username="default",
    password="pMVGQJK4owGqrnZgPCdOOnJwafZbi83N",
)

success = r.set('foo', 'bar')
# True

result = r.get('foo')
print(result)
# >>> bar

usuario_nome = "Mirela"
r.set("usuario:1", usuario_nome, ex=60)

print("Valor salvo:", r.get("usuario:1"))