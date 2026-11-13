"""Testa a sintaxe de filtro do REST do RM (somente GET, nada e gravado).

Uso: python tools/testar_rest.py [porta]     (padrao 8051)
"""
import os
import sys
from pathlib import Path
from urllib.parse import urlsplit

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

porta = sys.argv[1] if len(sys.argv) > 1 else "8051"
base = f"http://{urlsplit(os.environ['RM_URL']).hostname}:{porta}/rmsrestdataserver/rest/MovMovimentoTBCData"
auth = (os.environ["RM_USER"], os.environ["RM_PASS"])
# O RM le o filter como array JSON com a expressao SQL literal; colunas com prefixo TMOV.
# (o formato com "?" + valores falhou: "Quantidade de parametros ... nao corresponde")
filtros = [
    '["TMOV.IDMOV = 211266"]',
    '["TMOV.CODCOLIGADA = 1 AND TMOV.CODTMV = \'1.1.04\' AND TMOV.IDMOV = 211266"]',
    '["TMOV.CODCOLIGADA = 1 AND TMOV.CODTMV = \'1.1.04\' AND TMOV.IDINTEGRACAO = \'NAOEXISTE-XYZ\'"]',
]

for f in filtros:
    try:
        r = requests.get(base, params={"filter": f}, auth=auth, headers={"CODCOLIGADA": "1"}, timeout=90)
        try:
            d = r.json()
            dados = d.get("data")
            linhas = dados if isinstance(dados, list) else ([dados] if dados else [])
            achou = [(x.get("IDMOV"), x.get("NUMEROMOV")) for x in linhas][:5]
            print(f"{r.status_code} | {f}\n    length={d.get('length')} achou={achou} msgs={str(d.get('messages'))[:200]}")
        except ValueError:
            print(f"{r.status_code} | {f}\n    {r.text[:300]}")
    except Exception as e:
        print(f"ERRO | {f}\n    {e}")
