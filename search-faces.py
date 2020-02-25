import argparse
import boto3
import cv2
import json
import os
import datetime


BUCKET_NAME = os.environ["BUCKET_NAME"]
COLLECTION_ID = os.environ["COLLECTION_ID"]


def parse_args():
    p = argparse.ArgumentParser(description="rekognition demo")
    p.add_argument("--bucket-name", default=BUCKET_NAME, help="bucket name")
    p.add_argument("--collection-id", default=COLLECTION_ID, help="collection id")
    p.add_argument("--key", default="nalbam.jpg", help="key")
    return p.parse_args()


def main():
    args = parse_args()

    s3 = boto3.client("s3")

    if os.path.isdir("build") == False:
        os.mkdir("build")

    try:
        client = boto3.client("rekognition")
        res = client.search_faces_by_image(
            CollectionId=args.collection_id,
            Image={"S3Object": {"Bucket": args.bucket_name, "Name": args.key}},
            MaxFaces=1,
            FaceMatchThreshold=80,
        )
    except Exception as ex:
        print("Error", ex, args.key)
        res = []

    print(res)

    if res["SearchedFaceConfidence"] > 99:
        filename = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S.%f") + ".jpg"
        filepath = "build/{}".format(filename)

        s3.download_file(args.bucket_name, args.key, filepath)

        img = cv2.imread(filepath, cv2.IMREAD_COLOR)

        height = img.shape[0]
        width = img.shape[1]

        print(width, height)

        box = res["SearchedFaceBoundingBox"]

        rate = 0.03

        left = int(width * max(box["Left"] - rate, 0))
        top = int(height * max(box["Top"] - rate, 0))

        right = int(width * min(box["Left"] + box["Width"] + rate, 100))
        bottom = int(height * min(box["Top"] + box["Height"] + rate, 100))

        start = (left, top)
        end = (right, bottom)
        color = (255, 165, 20)
        thickness = 2

        cv2.rectangle(img, start, end, color, thickness)

        cv2.imwrite("{}.box.jpg".format(filepath), img)


if __name__ == "__main__":
    main()
