# 🍴 SNU 공대 식단 알림 봇 (SNU Menu Bot)

서울대학교 공대생(301동, 302동)의 편리한 식사를 위해, 매일 아침 식단 정보를 크롤링하여 이메일로 전송해주는 자동화 스크립트입니다.

## 🚀 주요 기능
- **Target**: 서울대학교 301동 식당(점심), 302동 식당(점심/저녁)
- **Filtering**: 301동의 불필요한 테이크아웃 및 카페 정보를 제외한 핵심 식단만 추출
- **Sorting**: 시간대별(점심/저녁)로 그룹화하여 가독성 높은 이메일 본문 생성
- **Automation**: GitHub Actions를 이용해 매일 오전 10시 30분(KST) 자동 실행
- **Smart Alert**: 주말이나 공휴일 등 식단 정보가 없는 날에는 이메일을 발송하지 않음

## 🛠️ 기술 스택
- **Language**: Python 3.10+
- **Library**: `requests`, `BeautifulSoup4`
- **Infrastructure**: GitHub Actions, Gmail SMTP

## ⚙️ 설정 방법 (Setup)

### 1. 환경 변수 (Secrets) 등록
GitHub Repository의 `Settings > Secrets and variables > Actions`에 아래 항목을 등록해야 합니다.
- `EMAIL_USER`: 발신용 Gmail 주소
- `EMAIL_PASSWORD`: Gmail 앱 비밀번호 (16자리)
- `RECEIVER_EMAIL`: 수신용 이메일 주소

### 2. 로컬 테스트
```powershell
# 의존성 설치
pip install requests beautifulsoup4

# 오늘 식단 확인
python main.py

# 특정 날짜 디버깅 (예: 2026-03-18)
python main.py -d 2026-03-18