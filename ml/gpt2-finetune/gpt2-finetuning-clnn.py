import gpt_2_simple as gpt2
import shutil
from google.cloud import bigquery
from google.cloud import storage

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))

client = bigquery.Client()

query = (
    "SELECT article FROM `climate-poc-01.clnn.news`"
)
query_job = client.query(
    query,
)

articles = ""
for row in query_job:
    articles = articles + row.article

textfile = open('clnn.txt', 'w')
textfile.write(articles)
textfile.close()

model_name = "124M"
gpt2.download_gpt2(model_name=model_name)   # model is saved into current directory under /models/124M/

sess = gpt2.start_tf_sess()
gpt2.finetune(sess,
              'clnn.txt',
              model_name=model_name,
              steps=5)   # steps is max number of training steps

# zip the model dir and upload to storage
shutil.make_archive('clnn-model', 'zip', 'checkpoint')
upload_blob("climate-poc-ml-models-bucket",'clnn-model.zip','clnn-model.zip')

gpt2.generate(sess)
