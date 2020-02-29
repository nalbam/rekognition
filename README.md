# rekognition

```bash
export STORAGE_NAME=rekognition-nalbam-demo

aws s3 mb s3://$STORAGE_NAME
aws rekognition create-collection --collection-id $STORAGE_NAME | jq .
```

```bash
aws rekognition create-collection --collection-id $STORAGE_NAME  | jq .

aws rekognition search-faces-by-image --collection-id $STORAGE_NAME \
--image-bytes fileb://images/iu.jpg | jq .

aws rekognition search-faces-by-image --collection-id doorman --region ap-northeast-1 \
--image-bytes fileb://images/nalbam.jpg | jq .
```
