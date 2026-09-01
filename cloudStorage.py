from google.cloud import storage

BUCKET_NAME = "TODO PUT A REAL NAME HERE"

def uploadToCloud(data, destinationBlobName:str, contentType:str = "text/plain", public:bool = False, bucketName:str = BUCKET_NAME) -> None|str:


    storageClient = storage.Client()
    bucket = storageClient.bucket(bucketName)
    blob = bucket.blob(destinationBlobName)

    blob.upload_from_string(data,contentType)

    if public:
        blob.make_public()
        return blob.public_url

def downloadFromCloudAsText(sourceBlobName, bucketName:str = BUCKET_NAME) -> str:

    storageClient = storage.Client()
    bucket = storageClient.bucket(bucketName)
    blob = bucket.blob(sourceBlobName)

    return blob.download_as_text()