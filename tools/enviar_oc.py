"""Envia a OC do arquivo 02 ao RM (com anti-duplicidade) e le de volta o que foi gravado.

Uso: python enviar_oc.py [caminho_do_xml]
"""
import os
import re
import sys
from pathlib import Path

from rm_ws import read_record, read_view, save_record

url = os.environ["RM_URL"] or sys.exit("Preencha RM_URL no .env")
arquivo = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent.parent / "02_SaveRecord_OC_teste.xml")
xml = re.search(r"<!\[CDATA\[(.*?)\]\]>", arquivo.read_text(encoding="utf-8"), re.S).group(1)
idint = re.search(r"<IDINTEGRACAO>(.*?)</IDINTEGRACAO>", xml).group(1)


def tag(x, name):
    m = re.search(rf"<{name}>(.*?)</{name}>", x, re.S)
    return m.group(1) if m else None


existente = read_view(url, f"TMOV.CODCOLIGADA=1 AND TMOV.CODTMV='1.1.04' AND TMOV.IDINTEGRACAO='{idint}'")
if "<TMOV>" in existente:
    sys.exit(f"Ja existe OC com IDINTEGRACAO={idint}: IDMOV={tag(existente, 'IDMOV')} "
             f"NUMEROMOV={tag(existente, 'NUMEROMOV')}. Nada enviado.")

print(f"Enviando OC {idint} para {url} ...")
retorno = save_record(url, xml)
print("Retorno SaveRecord:", retorno)
m = re.fullmatch(r"\s*1;(\d+)\s*", retorno)
if not m:
    sys.exit(1)

oc = read_record(url, f"1;{m.group(1)}")
for campo in ("IDMOV", "NUMEROMOV", "SERIE", "STATUS", "STSCOMPRAS", "CODCFO", "VALORLIQUIDO",
              "IDINTEGRACAO", "SEGUNDONUMERO", "USUARIOCRIACAO", "HISTORICOCURTO"):
    print(f"  {campo}: {tag(oc, campo)}")
print("  Itens:", len(re.findall("<TITMMOV>", oc)), "| rateio cabecalho:",
      re.findall(r"<TMOVRATCCU>.*?<VALOR>(.*?)</VALOR>", oc, re.S))
