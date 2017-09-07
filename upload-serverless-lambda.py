import boto3
import io
from io import StringIO
import zipfile
import mimetypes

def lambda_handler(event, context):
    s3 = boto3.resource('s3')

    serverless_bucket = s3.Bucket('ariane-serverless')
    build_bucket = s3.Bucket('ariane-serverless-build')

    serverless_zip = io.BytesIO()
    build_bucket.download_fileobj('serverlessbuild.zip', serverless_zip)

    with zipfile.ZipFile(serverless_zip) as myzip:
        for nm in myzip.namelist():
            obj = myzip.open(nm)
            serverless_bucket.upload_fileobj(obj, nm,
                ExtraArgs={'ContentType': mimetypes.guess_type(nm) [0]})
            serverless_bucket.Object(nm).Acl().put(ACL='public-read')
    
    return 'Hello from Lambda'