# 투자 신호등 (Mac 자동 수집 + GitHub Pages)

Mac이 하루 두 번(08:10, 15:40) 시세를 받아 `data.json`을 만들고 GitHub에 올립니다.
페이지(`index.html`)는 그 파일을 읽어 지표와 신호등을 보여줍니다. 주문 기능은 없습니다.

## 파일 구성
| 파일 | 역할 |
|---|---|
| `collector.py` | Yahoo Finance에서 시세를 받아 `data.json` 생성 |
| `collector_config.json` | 받을 종목 목록 (종목 추가·TIGER 종목코드 입력은 여기서) |
| `run.sh` | 수집 → GitHub 업로드 한 번에 실행 |
| `setup.sh` | 최초 1회. 가상환경 만들고 자동 실행 등록 |
| `index.html` | 화면 |
| `config.json` | 기준값·보유정보 (화면에서 저장하면 자동 생성, 모든 기기 공유) |
| `.github/workflows/collect.yml` | 폰에서 누르는 수동 수집 버튼 (선택) |

## 최초 설정 (약 30분)

**1. GitHub 준비**
- github.com 가입 → 우측 상단 `+` → New repository
- 이름 `signal`, **Public** 선택 → Create
- Settings → Developer settings → Personal access tokens → Fine-grained tokens → 새 토큰 생성
  (저장소는 `signal`만 선택, 권한 Contents: **Read and write**). 토큰은 복사해 둡니다.

**2. Mac 터미널에서** (응용 프로그램 → 유틸리티 → 터미널)
```
xcode-select --install
```
설치 창이 뜨면 완료될 때까지 기다립니다 (git, python3 설치).

**3. 이 폴더를 홈 폴더에 두고** (`~/signal-app`)
```
cd ~/signal-app
git init
git add .
git commit -m "init"
git branch -M main
git remote add origin https://github.com/내계정/signal.git
git push -u origin main
```
`push` 때 사용자명은 GitHub 계정, 비밀번호 칸에는 **위에서 만든 토큰**을 붙여넣습니다.
한 번 입력하면 Mac 키체인에 저장돼 이후 자동입니다.

**4. 페이지 켜기**
저장소 → Settings → Pages → Branch `main` / `/ (root)` → Save.
1~2분 뒤 `https://내계정.github.io/signal/` 로 열립니다.

**5. 자동 실행 등록 + 첫 수집**
```
./setup.sh
./run.sh
tail collector.log
```
`업로드 완료`가 보이면 성공입니다. 폰에서 주소를 열고 공유 → 홈 화면에 추가를 누르세요.

## 기기 간 동기화 설정 (폰·PC 각각 1회)
기준값과 보유정보는 이 저장소의 `config.json`에 저장돼서 어느 기기에서 열어도 같은 값이 보입니다.
- **읽기**는 토큰 없이 됩니다.
- **저장**하려면 그 기기에서 토큰을 한 번 넣어야 합니다: 페이지 → `기준 설정` → 맨 아래 `기기 간 동기화` → 토큰 붙여넣기 → 저장.
- 토큰은 1번에서 만든 것을 그대로 써도 됩니다 (Fine-grained, `signal` 저장소만, Contents 읽기·쓰기). 토큰은 그 기기 브라우저에만 저장됩니다.
- 폰과 PC에서 동시에 고치면 나중에 저장한 쪽이 이깁니다.
- 저장소가 공개라서 `config.json`(기준값, 보유 수량·평단)을 주소를 아는 누구나 읽을 수 있습니다.

## 폰에서 수집 실행 (선택)
GitHub 앱이나 브라우저 → `signal` 저장소 → Actions → `collect` → Run workflow.
GitHub 서버에서 수집하는 방식이라 Yahoo가 막을 수도 있습니다. 실패하면 Mac에서 `./run.sh`를 쓰세요.

## 자동 실행 동작
- 매일 08:10, 15:40(Mac 시간대가 한국일 때), 그리고 로그인·부팅 시 실행됩니다.
- 그 시각에 Mac이 잠자기 상태면 깨어난 뒤 실행됩니다. 전원이 꺼져 있으면 건너뜁니다.
- 선택: 잠자는 Mac을 미리 깨우려면 `sudo pmset repeat wakeorpoweron MTWRFSU 08:05:00`
  (덮개를 닫은 노트북은 깨어나지 않을 수 있습니다.)
- 해제: `launchctl bootout gui/$(id -u)/com.signal.collector`

## 자주 하는 수정
- **TIGER 종목 지정**: `collector_config.json`의 `"tiger"`에서 `yahoo`를 `"종목코드.KS"`로 (예: `"123456.KS"`), `name`도 원하는 이름으로.
- **업종·종목 추가/삭제**: 같은 파일의 `flow_groups`에서 `["티커","표시이름"]` 수정.
- **기준값(하락 %, 익절 % 등)**: 화면의 `기준 설정`에서 입력. 동기화 토큰이 있는 기기에서 저장하면 모든 기기에 반영됩니다.

## 문제가 생기면
- `collector.log` 마지막 줄을 확인하세요.
- `rate limited`가 보이면 Yahoo가 잠시 막은 것입니다. 몇 시간 뒤 다시 실행하면 대부분 풀립니다.
- 받지 못한 항목은 이전 값이 "이전값"으로 표시되고, 30시간 넘게 갱신이 없으면 화면에 경고가 뜹니다.

## 알아둘 점
- 시세 출처 yfinance는 비공식이라 언제든 깨질 수 있고, 개인 용도로만 쓰세요.
- 저장소가 공개라서 `data.json`(시장 데이터)과 `config.json`(기준값·보유 정보)이 모두 공개됩니다.
- 코스피 야간선물은 Yahoo에 없어 화면에서 직접 입력합니다 (이 값도 동기화됩니다).
- 신호는 정한 기준의 충족 여부만 보여주는 규칙 기반 참고 도구이며 투자 조언이 아닙니다.
