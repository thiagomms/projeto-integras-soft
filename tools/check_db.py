"""Teste de conexao (somente leitura) com o banco do RM definido no .env."""
import os
from pathlib import Path

import pyodbc
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 18 for SQL Server};"
    f"SERVER={os.environ['DB_SERVER']};DATABASE={os.environ['DB_DATABASE']};"
    f"UID={os.environ['DB_USERNAME']};PWD={os.environ['DB_PASSWORD']};"
    "TrustServerCertificate=yes;Encrypt=no;ApplicationIntent=ReadOnly",
    timeout=10,
)
cur = conn.cursor()
print("Banco/servidor:", cur.execute("SELECT DB_NAME(), @@SERVERNAME").fetchone())
print("Bancos no servidor:", [r[0] for r in cur.execute(
    "SELECT name FROM sys.databases WHERE name LIKE '%rasilia%' OR name LIKE '%orpore%'")])
print("OC modelo 211266:", cur.execute(
    "SELECT IDMOV, NUMEROMOV, CODTMV, VALORLIQUIDO FROM TMOV WHERE CODCOLIGADA=1 AND IDMOV=211266").fetchone())
print("Usuario de integracao:", cur.execute(
    "SELECT CODUSUARIO, NOME, STATUS FROM GUSUARIO WHERE CODUSUARIO=?", os.environ["RM_USER"]).fetchone())
print("OCs de teste ja criadas:", cur.execute(
    "SELECT COUNT(*) FROM TMOV WHERE CODCOLIGADA=1 AND IDINTEGRACAO LIKE 'SOFTEXPERT-TESTE-%'").fetchone()[0])
