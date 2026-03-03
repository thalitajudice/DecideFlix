import requests

# URL onde o seu Flask está rodando
BASE_URL = "http://127.0.0.1:5000"

print("🎬 === Iniciando Testes do Redis no Decide Flix === 🎬\n")

# --- 1. Teste do BITMAP ---
print("1️⃣ Testando BITMAP (Filmes Assistidos)...")
# Marcando filme de ID 45 como assistido pelo usuário 777
res_post_bit = requests.post(f"{BASE_URL}/usuarios/777/assistiu/45")
print(f"POST marcar assistido: {res_post_bit.json()}")

res_get_bit = requests.get(f"{BASE_URL}/usuarios/777/assistiu/45")
print(f"GET verificar assistido: {res_get_bit.json()}\n")


# --- 2. Teste do BLOOM FILTER ---
print("2️⃣ Testando BLOOM FILTER (Filmes Rejeitados)...")
# Rejeitando filme de ID 99 pelo usuário 777
res_post_bloom = requests.post(f"{BASE_URL}/usuarios/777/rejeitar/99")
print(f"POST rejeitar filme: {res_post_bloom.json()}")

res_get_bloom = requests.get(f"{BASE_URL}/usuarios/777/rejeitar/99")
print(f"GET verificar rejeitado: {res_get_bloom.json()}\n")


# --- 3. Teste do HYPERLOGLOG ---
print("3️⃣ Testando HYPERLOGLOG (Views Únicas)...")
# Simulando views no filme de ID 10
print("Registrando view do usuário 10...")
requests.post(f"{BASE_URL}/titulos/10/view/10")

print("Registrando view do usuário 20...")
requests.post(f"{BASE_URL}/titulos/10/view/20")

print("Registrando view do usuário 10 DE NOVO (o Redis não deve contar duplicado!)...")
requests.post(f"{BASE_URL}/titulos/10/view/10")

res_get_hll = requests.get(f"{BASE_URL}/titulos/10/views")
print(f"GET total de views únicas (deve ser 2): {res_get_hll.json()}\n")

print("✅ Testes finalizados! Pode comemorar!")