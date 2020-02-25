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

        src = cv2.imread(filepath, cv2.IMREAD_COLOR)

        height = src.shape[0]
        width = src.shape[1]

        print(width, height)

        box = res["SearchedFaceBoundingBox"]

        rate = 0.1
        w = box["Width"] * rate
        h = box["Height"] * rate

        start = (
            int(width * max(box["Left"] - w, 0)),
            int(height * max(box["Top"] - h, 0)),
        )
        end = (
            int(width * min(box["Left"] + box["Width"] + w, 100)),
            int(height * min(box["Top"] + box["Height"] + h, 100)),
        )

        dst = src.copy()
        dst = src[start[0] : (end[0] - start[0]), start[1] : (end[1] - start[1])]

        color = (255, 165, 20)
        thickness = 2

        cv2.rectangle(src, start, end, color, thickness)

        cv2.imwrite("{}.src.jpg".format(filepath), src)
        cv2.imwrite("{}.dst.jpg".format(filepath), dst)


if __name__ == "__main__":
    main()
