"""Descobre qual porta do RM.Host aponta para a base de TESTE (somente leitura)."""
import os
import re
import sys
from urllib.parse import urlsplit

sys.path.insert(0, __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0])
from check_db import cur  # noqa: E402  (conexao com Teste_BrasiliaSeg)
from rm_ws import read_record  # noqa: E402

idmov, numero, criado = cur.execute(
    "SELECT TOP 1 IDMOV, NUMEROMOV, CONVERT(varchar(19), DATACRIACAO, 126) FROM TMOV "
    "WHERE CODCOLIGADA=1 ORDER BY IDMOV DESC").fetchone()
print(f"\nNo banco de teste: maior IDMOV={idmov} NUMEROMOV={numero} DATACRIACAO={criado}\n")

def tag(xml, name):
    m = re.search(rf"<{name}>(.*?)</{name}>", xml)
    return m.group(1) if m else None

RM_HOST = urlsplit(os.environ["RM_URL"]).hostname  # vem do .env

for porta in (8051, 8053, 8055, 8057):
    url = f"http://{RM_HOST}:{porta}"
    try:
        for pk in (idmov, idmov + 1):
            xml = read_record(url, f"1;{pk}")
            print(f"{porta} IDMOV {pk}: NUMEROMOV={tag(xml, 'NUMEROMOV')} "
                  f"DATACRIACAO={tag(xml, 'DATACRIACAO')} TMOV={'<TMOV>' in xml}")
    except Exception as e:
        print(f"{porta}: ERRO {str(e)[:300]}")
