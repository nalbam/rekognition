# rekognition

```bash
export BUCKET_NAME=rekognition-nalbam-demo
export COLLECTION_ID=rekognition-nalbam-demo

aws s3 mb s3://$BUCKET_NAME
aws rekognition create-collection --collection-id $COLLECTION_ID | jq .
```

```bash
aws rekognition create-collection --collection-id $COLLECTION_ID  | jq .

aws rekognition search-faces-by-image --collection-id $COLLECTION_ID \
--image-bytes fileb://images/iu.jpg | jq .

aws rekognition search-faces-by-image --collection-id doorman --region ap-northeast-1 \
--image-bytes fileb://images/nalbam.jpg | jq .

```
