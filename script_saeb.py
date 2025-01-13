import basedosdados as bd
import boto3
from datetime import datetime
import pyarrow as pa
import pyarrow.parquet as pq
from io import BytesIO

# variáveis da chamada
dataset_id = 'br_inep_saeb'
table_id_2ano = 'aluno_ef_2ano'

# baixando através do bq
df = bd.read_table(
    dataset_id=dataset_id,
    table_id=table_id_2ano,
    billing_project_id = 'project-saeb', # lembrar de criar conexão com a service-account
    reauth=True  
)

# convertendo para .parquet
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
