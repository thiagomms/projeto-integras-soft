"""Cliente minimo do wsDataServer do RM (SOAP), configurado pelo .env."""
import os
import re
from html import escape, unescape
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

NS = "http://www.totvs.com/"


def _call(url, action, body):
    envelope = (
        '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" '
        f'xmlns:tot="{NS}"><soapenv:Header/><soapenv:Body>{body}</soapenv:Body></soapenv:Envelope>'
    )
    resp = requests.post(
        f"{url}/wsDataServer/IwsDataServer",
        data=envelope.encode("utf-8"),
        headers={"Content-Type": "text/xml; charset=utf-8",
                 "SOAPAction": f'"{NS}IwsDataServer/{action}"'},
        auth=(os.environ["RM_USER"], os.environ["RM_PASS"]),
        timeout=60,
    )
    m = re.search(rf"<{action}Result>(.*)</{action}Result>", resp.text, re.S)
    if resp.status_code != 200 or not m:
        raise RuntimeError(f"HTTP {resp.status_code}: {unescape(resp.text)[:2000]}")
    return unescape(m.group(1))


def contexto():
    return f"CODCOLIGADA=1;CODFILIAL=1;CODSISTEMA=T;CODUSUARIO={os.environ['RM_USER']}"


def read_record(url, primary_key, dataserver="MovMovimentoTBCData"):
    return _call(url, "ReadRecord",
                 f"<tot:ReadRecord><tot:DataServerName>{dataserver}</tot:DataServerName>"
                 f"<tot:PrimaryKey>{primary_key}</tot:PrimaryKey>"
                 f"<tot:Contexto>{contexto()}</tot:Contexto></tot:ReadRecord>")


def read_view(url, filtro, dataserver="MovMovimentoTBCData"):
    return _call(url, "ReadView",
                 f"<tot:ReadView><tot:DataServerName>{dataserver}</tot:DataServerName>"
                 f"<tot:Filtro>{escape(filtro)}</tot:Filtro>"
                 f"<tot:Contexto>{contexto()}</tot:Contexto></tot:ReadView>")


def save_record(url, xml, dataserver="MovMovimentoTBCData"):
    """Grava no RM. Sucesso retorna 'CODCOLIGADA;IDMOV'; erro retorna o texto da excecao."""
    return _call(url, "SaveRecord",
                 f"<tot:SaveRecord><tot:DataServerName>{dataserver}</tot:DataServerName>"
                 f"<tot:XML><![CDATA[{xml}]]></tot:XML>"
                 f"<tot:Contexto>{contexto()}</tot:Contexto></tot:SaveRecord>")
