# ⚾ YBL의 세번째 AI 서비스, YIPP x KBO AI 투자 리포트

> **"현재가지 당신의 투자 성적표를 공개합니다."**
> 핀테크 서비스 **YIPP**과 한국 프로야구 **KBO**가 함께 제공하는 연말 결산 AI 리포트 서비스입니다.
> 사용자의 1년 간 투자 기록을 분석하여, 마치 스포츠 신문의 1면 기사나 스카우팅 리포트처럼 생생한 **인포그래픽 리포트**를 생성해줍니다.

👉 **Live Demo:** [https://yipp-report.streamlit.app/](https://yipp-report.streamlit.app/)

---

## 📅 1. 기획 배경

단순히 숫자만 나열된 딱딱한 투자 결산 대신, 사용자가 자신의 투자 성과를 **직관적이고 재미있게 확인하고 SNS에 자랑할 수 있는 콘텐츠**를 제공하기 위해 기획되었습니다.

### 💡 핵심 컨셉
* **Visual Storytelling:** 복잡한 투자 기록을 한 장의 세련된 포스터(인포그래픽)로 압축하여 전달합니다.
* **Highlighting Success:** 가장 높은 수익률을 기록한 '효자 종목'을 강조하여 투자자에게 성취감을 부여합니다.
* **Shareable Content:** 인스타그램 스토리 사이즈(9:16)에 최적화된 결과물을 제공하여 자연스러운 SNS 공유를 유도합니다.

---

## 🛠 2. 주요 기능

### 1️⃣ 선수 정보 인증 및 조회
* **본인 확인:** 이름과 계좌번호 인증을 통해 개인화된 투자 데이터(`customer_report_updated.csv`)에 안전하게 접근합니다. 해당 데이터는 실제 유안타증권 고객 데이터가 아닌, AI서비스 구현을 위해 제작된 가상 YBL 참여자 데이터입니다.

### 2️⃣ 투자 지표 분석
* **5-Factor Radar Chart:** 투자의 5대 요소(거래금액, 안정성, 분산투자, 거래빈도, 해외비중)를 오각형 그래프로 시각화합니다.
* **Moneyball Stats:** 투자 지표를 야구 스탯으로 치환하여 재미를 더했습니다.

### 3️⃣ AI 투자 리포트 생성
* Google Gemini (gemini-3-pro-image-preview) 모델을 활용합니다.
    * **커스텀 캐릭터:** 응원 구단 유니폼을 입은 사용자의 뒷모습 일러스트.
    * **데이터 시각화:** 분석된 5가지 지표가 반영된 레이더 차트.
    * **Hall of Fame:** 수익률 Top 3 종목과 구체적인 수익률 수치(%) 표기.
    * **브랜딩:** YIPP 로고 및 테마 컬러 적용.

---

## 🏗 3. 기술 스택

### Frontend & Application
* **Streamlit:** Python으로 인터랙티브한 애플리케이션 UI를 구현했습니다.
* **Responsive Layout:** 모바일 환경에서도 쾌적하게 이용할 수 있도록 UI 구성.

### Data Processing
* **Pandas:** 고객 데이터를 효율적으로 로드합니다.

### Artificial Intelligence
* **Google GenAI SDK (v1.0):** Gemini 모델을 통해 프롬프트를 고퀄리티 이미지로 변환합니다.
* **Context-Aware Prompting:** 사용자의 투자 성향과 보유 종목, 수익률 등의 데이터를 자연어 프롬프트에 문맥에 맞게 삽입하여 정확한 정보가 담기도록 설계합니다.

---

## 🖼️ 도식화
<img width="1024" height="590" alt="image" src="https://github.com/user-attachments/assets/de138fa7-3dce-4ac4-bb2f-bbdd7bee3574" />

