#!/bin/bash
# 시세 수집 -> data.json -> GitHub 업로드
cd "$(dirname "$0")" || exit 1
exec >> collector.log 2>&1
echo "=== $(date '+%Y-%m-%d %H:%M:%S') 실행 ==="
source .venv/bin/activate || exit 1
python collector.py || { echo "수집 실패"; exit 1; }
git add data.json
if git diff --cached --quiet; then echo "변경 없음"; exit 0; fi
git commit -q -m "data: $(date '+%Y-%m-%d %H:%M')"
git pull --rebase --autostash -q
git push -q && echo "업로드 완료" || echo "업로드 실패"
