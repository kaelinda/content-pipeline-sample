#!/usr/bin/env python3
"""把图片/视频上传到 S3 兼容对象存储并登记（纯标准库实现 SigV4）。
未配置 OSS 环境变量时走 staging 模式：文件放 assets-staging/，manifest 记 pending。"""
import argparse, os, sys, json, hashlib, datetime, shutil, urllib.request, hmac, mimetypes

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fm import parse, set_fields

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def sha256(b):
    return hashlib.sha256(b).hexdigest()

def sign(key, msg):
    return hmac.new(key, msg.encode(), hashlib.sha256).digest()

def sigv4_put(endpoint, bucket, key, data, ctype):
    ak = os.environ["OSS_ACCESS_KEY_ID"]
    sk = os.environ["OSS_ACCESS_KEY_SECRET"]
    # R2 的 SigV4 region 必须是 auto；未显式配置时按 endpoint 推断，COS/OSS 仍沿用 ap-shanghai 兜底
    region = os.environ.get("OSS_REGION") or ("auto" if "r2.cloudflarestorage.com" in endpoint else "ap-shanghai")
    host = endpoint.replace("https://", "").replace("http://", "").rstrip("/")
    now = datetime.datetime.now(datetime.timezone.utc)
    amzdate = now.strftime("%Y%m%dT%H%M%SZ")
    datestamp = now.strftime("%Y%m%d")
    payload_hash = sha256(data)
    uri = "/" + bucket + "/" + key
    headers = {"host": host, "x-amz-content-sha256": payload_hash, "x-amz-date": amzdate, "content-type": ctype}
    signed = ";".join(sorted(headers))
    nl = chr(10)
    canon_headers = "".join(k + ":" + headers[k] + nl for k in sorted(headers))
    canon = "PUT" + nl + uri + nl + nl + canon_headers + nl + signed + nl + payload_hash
    scope = datestamp + "/" + region + "/s3/aws4_request"
    tosign = "AWS4-HMAC-SHA256" + nl + amzdate + nl + scope + nl + sha256(canon.encode())
    k = sign(("AWS4" + sk).encode(), datestamp)
    k = sign(k, region)
    k = sign(k, "s3")
    k = sign(k, "aws4_request")
    sig = hmac.new(k, tosign.encode(), hashlib.sha256).hexdigest()
    headers["Authorization"] = "AWS4-HMAC-SHA256 Credential=" + ak + "/" + scope + ", SignedHeaders=" + signed + ", Signature=" + sig
    req = urllib.request.Request("https://" + host + uri, data=data, method="PUT", headers=headers)
    with urllib.request.urlopen(req, timeout=60) as r:
        if r.status not in (200, 201):
            raise RuntimeError("upload HTTP " + str(r.status))

ap = argparse.ArgumentParser()
ap.add_argument("--topic", required=True)
ap.add_argument("--type", required=True)
ap.add_argument("--file", required=True)
a = ap.parse_args()

data = open(a.file, "rb").read()
digest = sha256(data)
ext = os.path.splitext(a.file)[1].lower() or ".bin"
key = "assets/" + a.topic + "/" + a.type + "-" + digest[:8] + ext
configured = all(os.environ.get(k2) for k2 in ("OSS_ENDPOINT", "OSS_BUCKET", "OSS_ACCESS_KEY_ID", "OSS_ACCESS_KEY_SECRET"))
if configured:
    ctype = mimetypes.guess_type(a.file)[0] or "application/octet-stream"
    sigv4_put(os.environ["OSS_ENDPOINT"], os.environ["OSS_BUCKET"], key, data, ctype)
    base = os.environ.get("OSS_PUBLIC_BASE") or (os.environ["OSS_ENDPOINT"].rstrip("/") + "/" + os.environ["OSS_BUCKET"])
    url = base.rstrip("/") + "/" + key
    status = "uploaded"
else:
    dest = os.path.join(root, "assets-staging", a.topic, os.path.basename(key))
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copyfile(a.file, dest)
    url = "staging://" + a.topic + "/" + os.path.basename(key)
    status = "pending"

rec = {"topic_id": a.topic, "type": a.type, "url": url, "sha256": digest, "name": os.path.basename(a.file),
       "registered_at": datetime.date.today().isoformat(), "upload_status": status, "key": key}
with open(os.path.join(root, "assets/manifest.jsonl"), "a", encoding="utf-8") as f:
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")

for folder in ("topics", "articles"):
    p = os.path.join(root, folder, a.topic + ".md")
    if os.path.exists(p):
        t = open(p, encoding="utf-8").read()
        d, _ = parse(t)
        assets = d.get("assets") or []
        if url not in assets:
            assets.append(url)
        open(p, "w", encoding="utf-8").write(set_fields(t, {"assets": assets}))
print(status + ": " + url)
