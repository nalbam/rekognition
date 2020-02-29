import argparse
import boto3
import cv2
import datetime
import hashlib
import json
import os


STORAGE_NAME = os.environ["STORAGE_NAME"]

LINE_COLOR = (255, 165, 20)
LINE_WIDTH = 2


def parse_args():
    p = argparse.ArgumentParser(description="rekognition demo")
    p.add_argument("--bucket-name", default=STORAGE_NAME, help="bucket name")
    p.add_argument("--collection-id", default=STORAGE_NAME, help="collection id")
    p.add_argument("--key", default="nalbam.jpg", help="key")
    return p.parse_args()


def crop(src_path, dst_path, box):
    src = cv2.imread(src_path, cv2.IMREAD_COLOR)

    left, top, right, bottom = get_bounding_box(src.shape[1], src.shape[0], box)

    # crop
    dst = src.copy()
    dst = src[top:bottom, left:right]

    cv2.imwrite("{}.dst.jpg".format(dst_path), dst)


def rectangle(src_path, dst_path, box):
    src = cv2.imread(src_path, cv2.IMREAD_COLOR)

    left, top, right, bottom = get_bounding_box(src.shape[1], src.shape[0], box)

    # rectangle
    color = LINE_COLOR
    thickness = LINE_WIDTH

    cv2.rectangle(src, (left, top), (right, bottom), color, thickness)

    cv2.imwrite(dst_path, src)


def get_bounding_box(width, height, box, rate=0.1):
    rw = box["Width"] * rate
    rh = box["Height"] * rate

    left = int(width * max(box["Left"] - rw, 0))
    top = int(height * max(box["Top"] - rh, 0))

    right = int(width * min(box["Left"] + box["Width"] + rw, 100))
    bottom = int(height * min(box["Top"] + box["Height"] + rh, 100))

    return left, top, right, bottom


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
        dt = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S.%f")

        hashkey = hashlib.md5(dt).hexdigest()

        src_path = "{}/{}-{}.jpg".format("build", hashkey, "src")
        crp_path = "{}/{}-{}.jpg".format("build", hashkey, "crp")
        box_path = "{}/{}-{}.jpg".format("build", hashkey, "box")

        s3.download_file(args.bucket_name, args.key, src_path)

        crop(src_path, crp_path, res["SearchedFaceBoundingBox"])

        rectangle(src_path, box_path, res["SearchedFaceBoundingBox"])


if __name__ == "__main__":
    main()
