#!/usr/bin/env python3
"""
CI deploy 后闸门：用 GitHub release asset 的真实 digest/size 校正 pacman db。

根因：多个 shard 并发部署时，softprops/action-gh-release 上传同名包会覆盖 asset，
而各 shard 生成的 db 基于自己抓取的旧 db，导致 db 里的 %SHA256SUM%/%CSIZE%
与 release 上实际资产不一致 → 客户端 pacman 报「檔案毀損(資料庫不正確或損毀（檢查碼）)」。

本脚本不下载任何包，只重写 db 内 desc 文本的两个字段，然后通过 API 覆盖上传
 junlin03-aur.db 与 .db.tar.gz。权威来源 = GitHub API assets[].digest / .size。
"""
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import time

REPO = os.environ.get("GH_REPO", "Capricornus007/repo")
TAG = os.environ.get("REPO_RELEASE_TAG", "current-repo")
DB = "deploy/junlin03-aur.db"
OUT = "deploy/junlin03-aur-fixed.db"


def api_json(path):
    r = subprocess.run(["gh", "api", path], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"gh api {path}: {r.stderr.strip()[:200]}")
    return json.loads(r.stdout)


def get_release():
    for i in range(1, 6):
        try:
            return api_json(f"repos/{REPO}/releases/tags/{TAG}")
        except Exception as e:
            print(f"取 release 重试 {i}: {e}", file=sys.stderr)
            time.sleep(4 * i)
    raise SystemExit("取不到 release，拒绝修正 db")


def upload_asset(rid, name, path):
    token = os.environ.get("GH_TOKEN", "")
    if not token:
        raise SystemExit("GH_TOKEN 未设置")
    # 先删同名旧 asset（--clobber 在部分 gh 版本不可靠，显式删更稳）
    rel = api_json(f"repos/{REPO}/releases/tags/{TAG}")
    for a in rel.get("assets", []):
        if a["name"] == name:
            d = subprocess.run(
                ["gh", "api", "-X", "DELETE", f"repos/{REPO}/releases/assets/{a['id']}"],
                capture_output=True, text=True,
            )
            if d.returncode != 0:
                print(f"删除旧 asset {name} 失败: {d.stderr.strip()[:120]}", file=sys.stderr)
    cmd = [
        "curl", "-sS", "-X", "POST",
        "-H", "Authorization: Bearer " + token,
        "-H", "Content-Type: application/octet-stream",
        "--data-binary", "@" + path,
        f"https://uploads.github.com/repos/{REPO}/releases/{rid}/assets?name={name}",
        "--max-time", "180",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    try:
        j = json.loads(r.stdout)
    except ValueError:
        raise SystemExit(f"上传 {name} 返回非 JSON: {r.stdout[:200]} {r.stderr[:200]}")
    if j.get("state") != "uploaded":
        raise SystemExit(f"上传 {name} 失败: {j.get('message', r.stdout[:200])}")
    print(f"上传 {name}: {j.get('digest')}")


def main():
    if not os.path.isfile(DB):
        raise SystemExit(f"找不到 {DB}")

    rel = get_release()
    rid = rel["id"]
    assets = {}
    for a in rel.get("assets", []):
        sha = a.get("digest") or ""
        if sha.startswith("sha256:") and len(sha) == 71:
            assets[a["name"]] = (sha[7:], str(a["size"]))
    print(f"权威 asset 数: {len(assets)}")

    changed_sha = 0
    changed_size = 0
    missing = 0
    buf = io.BytesIO()
    with tarfile.open(DB, "r:gz") as tin, tarfile.open(fileobj=buf, mode="w:gz") as tout:
        for m in tin.getmembers():
            data = tin.extractfile(m).read() if m.isfile() else b""
            if m.isfile() and m.name.endswith("/desc"):
                txt = data.decode("utf-8", "replace")
                fm = re.search(r"%FILENAME%\n(.+)", txt)
                if fm:
                    fname = fm.group(1).strip()
                    if fname in assets:
                        real_sha, real_size = assets[fname]
                        mo_sha = re.search(r"%SHA256SUM%\n(.+)", txt)
                        mo_size = re.search(r"%CSIZE%\n(.+)", txt)
                        if mo_sha and mo_sha.group(1).strip() != real_sha:
                            txt = re.sub(r"(%SHA256SUM%\n).+", lambda x: x.group(1) + real_sha, txt, count=1)
                            changed_sha += 1
                        if mo_size and mo_size.group(1).strip() != real_size:
                            txt = re.sub(r"(%CSIZE%\n).+", lambda x: x.group(1) + real_size, txt, count=1)
                            changed_size += 1
                        data = txt.encode("utf-8")
                    else:
                        missing += 1
            nm = tarfile.TarInfo(m.name)
            nm.size = len(data)
            nm.mtime = m.mtime
            nm.mode = m.mode
            nm.uid = m.uid
            nm.gid = m.gid
            nm.uname = m.uname
            nm.gname = m.gname
            nm.type = m.type
            tout.addfile(nm, io.BytesIO(data) if m.isfile() else None)

    with open(OUT, "wb") as f:
        f.write(buf.getvalue())
    print(f"校正 SHA256: {changed_sha} 条, CSIZE: {changed_size} 条, 不在 release: {missing} 条")

    if changed_sha == 0 and changed_size == 0:
        print("db 已与 release asset 一致，无需覆盖上传")
        return

    # 覆盖上传 .db 与 .db.tar.gz（pacman 客户端按 Server 取 .db，CI 也发布 .db.tar.gz）
    upload_asset(rid, "junlin03-aur.db", OUT)
    upload_asset(rid, "junlin03-aur.db.tar.gz", OUT)
    # 同步本地 deploy/ 里的 db，供后续「清理旧版本」step 使用同一口径
    import shutil
    shutil.copyfile(OUT, DB)
    shutil.copyfile(OUT, "deploy/junlin03-aur.db.tar.gz")
    print("本地 deploy db 已同步为修正版本")


if __name__ == "__main__":
    main()
