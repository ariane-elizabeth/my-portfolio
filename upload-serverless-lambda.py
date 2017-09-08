#update lambda permissions to allow to print to cloudwatch logs.

import boto3
import io
from io import StringIO
import zipfile
import mimetypes

def lambda_handler(event, context):
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:eu-west-1:226342546049:ariane-serverless-topic')
    
    location = {
        "bucketName": 'ariane-serverless-build',
        "objectKey": 'serverlessbuild.zip'
    }
    try:
        job = event.get("CodePipeline.job")
        
        if job:
            for artifact in job["data"]["inputArtifacts"]:
                if artifact["name"] == "MyAppBuild":
                    location = artifact["location"]["s3Location"]
        
        s3 = boto3.resource('s3')
        
        serverless_bucket = s3.Bucket('ariane-serverless')
        build_bucket = s3.Bucket(location["bucketName"])
    
        serverless_zip = io.BytesIO() #had to use Bytes rather than String as using Python3. What is StringIO for?
        build_bucket.download_fileobj(location["objectKey"], serverless_zip)
    
        with zipfile.ZipFile(serverless_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                serverless_bucket.upload_fileobj(obj, nm,
                    ExtraArgs={'ContentType': mimetypes.guess_type(nm) [0]}) #what is this bit for?
                serverless_bucket.Object(nm).Acl().put(ACL='public-read') #makes the bucket public
        
        topic.publish(Subject="Serverless deployed", Message="Serverless deployed successfully!")
        if job:
            codepipeline = boto3.client('codepipeline')
            codepipeline.put_job_success_result(jobId=job["id"])
        
    except:
        topic.publish(Subject="Serverless Deploy Failed", Message="The serverless was not deployed successfully.")
        raise

    print("Job done!")
    
    return 'Hello from Lambda'
    
    