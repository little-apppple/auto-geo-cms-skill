#!/usr/bin/env python3
"""verify_git.py - verify local read+write access to a git repo, loop until OK.

Usage:
  python scripts/verify_git.py --repo <url> --path <localPath> [--branch main]

Exit codes:
  0  READ_OK + WRITE_OK
  2  clone failed
  3  read (fetch) failed
  4  write (push) failed
"""
import argparse
import os
import subprocess
import sys


def run(cmd, cwd=None, timeout=120):
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except Exception as e:  # pragma: no cover
        return 1, "", str(e)


def is_repo(path):
    return os.path.isdir(os.path.join(path, ".git"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--path", default=".")
    ap.add_argument("--branch", default=None)
    args = ap.parse_args()

    path = os.path.abspath(args.path)
    os.makedirs(path, exist_ok=True)

    # 1) clone if needed
    if not is_repo(path):
        print(f"[1/4] 克隆仓库 {args.repo} -> {path}")
        rc, out, err = run(["git", "clone", args.repo, path])
        if rc != 0:
            print("CLONE_FAIL")
            print((err or out).strip())
            sys.exit(2)
    else:
        print("[1/4] 已存在仓库，跳过克隆")

    # 2) determine branch
    branch = args.branch
    if not branch:
        rc, out, _ = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=path)
        branch = out.strip() or "main"
    print(f"[2/4] 分支={branch}")

    # 3) read check: fetch
    print("[3/4] 读取权限探测: git fetch")
    rc, out, err = run(["git", "fetch", "origin", branch], cwd=path)
    if rc != 0:
        print("READ_FAIL")
        msg = (err or out).strip()
        if "publickey" in msg:
            print("原因: SSH 公钥未加入托管平台，请添加本机公钥后重试。")
        elif "Repository not found" in msg:
            print("原因: 仓库地址错误或无访问权限。")
        elif "Username" in msg:
            print("原因: HTTPS 缺少凭据 / token。")
        else:
            print(msg)
        sys.exit(3)
    print("READ_OK")

    # 4) write check: push dry-run (non-destructive)
    print("[4/4] 写入权限探测: git push --dry-run")
    rc, out, err = run(["git", "push", "--dry-run", "origin", branch], cwd=path)
    if rc != 0:
        rc2, out2, err2 = run(
            ["git", "push", "--dry-run", "-u", "origin", branch], cwd=path
        )
        if rc2 != 0:
            print("WRITE_FAIL")
            msg = (err2 or out2 or err or out).strip()
            if "permission denied" in msg.lower() or "remote rejected" in msg:
                print("原因: 账号无写权限，请申请写权限后重试。")
            else:
                print(msg)
            sys.exit(4)
    print("WRITE_OK")
    print("GIT_VERIFIED")
    sys.exit(0)


if __name__ == "__main__":
    main()
