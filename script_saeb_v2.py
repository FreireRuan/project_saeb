import pandas as pd
import boto3
from google.cloud import bigquery
from google.oauth2 import service_account
from datetime import datetime
import pyarrow as pa
import pyarrow.parquet as pq
from io import BytesIO

# Defina o caminho para sua chave de conta de serviço
service_account_path = r'C:\sandbox_ruan_morais\project-saeb-49bf6a6cf71b.json'

# Carregar as credenciais da conta de serviço
credentials = service_account.Credentials.from_service_account_file(service_account_path)

# Configurar o cliente do BigQuery usando as credenciais
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

# variáveis da chamada
project = 'basedosdados'
dataset_id = 'br_inep_saeb'
table_id_2ano = 'aluno_ef_2ano'

# Consulta para obter os dados da tabela
query = f"""
    SELECT * FROM `{project}.{dataset_id}.{table_id_2ano}`
"""

# Executar a consulta e armazenar os resultados em um DataFrame
df = client.query(query).to_dataframe()

# Convertendo para .parquet
table = pa.Table.from_pandas(df)

# variáveis datas para particionamento
current_date = datetime.now()
year = current_date.year
month = current_date.month
day = current_date.day

# buffer do arquivo
buffer = BytesIO()

# salvando em parquet
pq.write_table(table, buffer)
buffer.seek(0)

# crendeciais da aws
s3_client = boto3.client('s3', region_name='us-east-1')

# definindo caminho
# bucket_name = 's3://project-saeb/saeb/'
bucket_name = 'project-saeb'
s3_path = f'saeb/{year}/{month:02d}/{day:02d}/aluno_ef_2ano.parquet'

# enviando para o s3
s3_client.upload_fileobj(buffer, bucket_name, s3_path)

print(f"Arquivo enviado com sucesso para s3://{bucket_name}/{s3_path}")
