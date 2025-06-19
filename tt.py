import time

import requests

list_users = [
  { "email": "joice.oliveira@email.com", "password": "Senha@123", "tax_id": "33554507822" },
  { "email": "wilson.silva@email.com", "password": "Senha@123", "tax_id": "35737691870" },
  { "email": "celso.cordeiro@email.com", "password": "Senha@123", "tax_id": "22975285825" },
  { "email": "luciana.nascimento@email.com", "password": "Senha@123", "tax_id": "29130385814" },
  { "email": "andre.luis@email.com", "password": "Senha@123", "tax_id": "13254573889" },
  { "email": "carlos.rodrigues@email.com", "password": "Senha@123", "tax_id": "8760633859" },
  { "email": "alessandra.silva@email.com", "password": "Senha@123", "tax_id": "29271123808" },
  { "email": "naiara.mariano@email.com", "password": "Senha@123", "tax_id": "45840374857" },
  { "email": "sandra.gouvea@email.com", "password": "Senha@123", "tax_id": "12256563898" },
  { "email": "catia.santana@email.com", "password": "Senha@123", "tax_id": "8870904865" },
  { "email": "glaucia.rosa@email.com", "password": "Senha@123", "tax_id": "16180096805" },
  { "email": "cassia.campos@email.com", "password": "Senha@123", "tax_id": "41476225850" },
  { "email": "regina.toledo@email.com", "password": "Senha@123", "tax_id": "16098306877" },
  { "email": "tatiane.freire@email.com", "password": "Senha@123", "tax_id": "36518775823" },
  { "email": "glaucia.oliveira@email.com", "password": "Senha@123", "tax_id": "27272945818" },
  { "email": "leandro.godoi@email.com", "password": "Senha@123", "tax_id": "9751786606" },
  { "email": "matheus.santana@email.com", "password": "Senha@123", "tax_id": "32966544880" }
]

url = "https://apis-backend-meuinquilino-dev-zihvqe-b98e2e-146-235-36-168.traefik.me/v1/users/register/"
headers = {
    "Content-Type": "application/json",
    "User-Agent": "insomnia/11.0.2"
}

respostas = []

for user in list_users:
    payload = {
        "email": user["email"],
        "password": "Senha@123",
        "tax_id": user["tax_id"]
    }

    try:
        response = requests.post(url, json=payload, headers=headers, verify=False)
        print(f"{user['email']} -> {response.status_code}: {response.text}")
        respostas.append({
            "email": user["email"],
            "status": response.status_code,
            "response": response.text
        })
    except Exception as e:
        print(f"Erro ao cadastrar {user['email']}: {e}")
        respostas.append({
            "email": user["email"],
            "status": "erro",
            "response": str(e)
        })
