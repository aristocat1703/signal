#!/bin/bash
# 최초 1회: 가상환경 생성 + 매일 자동 실행 등록 (macOS)
set -e
cd "$(dirname "$0")"
DIR="$(pwd)"
python3 -m venv .venv
source .venv/bin/activate
pip install -q -r requirements.txt
chmod +x run.sh
PLIST="$HOME/Library/LaunchAgents/com.signal.collector.plist"
mkdir -p "$HOME/Library/LaunchAgents"
cat > "$PLIST" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.signal.collector</string>
  <key>ProgramArguments</key><array><string>/bin/bash</string><string>$DIR/run.sh</string></array>
  <key>StartCalendarInterval</key><array>
    <dict><key>Hour</key><integer>8</integer><key>Minute</key><integer>10</integer></dict>
    <dict><key>Hour</key><integer>15</integer><key>Minute</key><integer>40</integer></dict>
  </array>
  <key>RunAtLoad</key><true/>
</dict></plist>
PL
launchctl bootout "gui/$(id -u)/com.signal.collector" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
echo "완료: 매일 08:10, 15:40(Mac 시간 기준)과 로그인 시 실행됩니다."
echo "지금 바로 한 번 실행해보려면: ./run.sh 후 tail collector.log"
