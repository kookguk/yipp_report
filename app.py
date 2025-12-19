import streamlit as st
from io import BytesIO
from PIL import Image
import base64
import os
import time
import pandas as pd
import numpy as np

# ✅ Google GenAI SDK (v1.0 최신 버전)
from google import genai
from google.genai import types

# -----------------------------
# 0. 페이지 기본 설정
# -----------------------------
st.set_page_config(
    page_title="YIPP X KBO AI 투자리포트",
    page_icon="logo.png",
    layout="centered"
)

# -----------------------------
# 1. Gemini Client 초기화
# -----------------------------
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except KeyError:
    st.error("❌ `.streamlit/secrets.toml` 파일에 `GEMINI_API_KEY`가 없습니다.")
    st.stop()
except Exception as e:
    st.error(f"❌ 클라이언트 연결 오류: {e}")
    st.stop()


# -----------------------------
# 상수 및 설정
# -----------------------------
KBO_TEAMS = [
    "SSG 랜더스", "롯데 자이언츠", "KIA 타이거즈", "삼성 라이온즈", "한화 이글스",
    "두산 베어스", "LG 트윈스", "KT 위즈", "NC 다이노스", "키움 히어로즈"
]

REFERENCE_IMAGE_PATH = "image.png" # 레퍼런스 이미지 (리포트 스타일)
LOGO_DIR = "logos"
CSV_FILE_PATH = "customer_report_updated.csv" # 업데이트된 CSV 파일 사용

# 테마 컬러 정의 (민트색)
THEME_COLOR = "#008F53"


# -----------------------------
# 세션 상태 초기화
# -----------------------------
def init_session_state():
    defaults = {
        "step": 1,
        "player_data": None,    # CSV에서 가져온 사용자 데이터 행
        "team": None,
        "player_name": "",      
        "account": "",
        "number": None,
        "position": None,
        "report_image_bytes": None, # 리포트 이미지 저장
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session_state()


# -----------------------------
# 유틸리티 함수
# -----------------------------
def load_reference_bytes():
    try:
        with open(REFERENCE_IMAGE_PATH, "rb") as f:
            return f.read()
    except FileNotFoundError:
        return None

def load_and_resize_logo(team_name, size=(80, 80)):
    path = os.path.join(LOGO_DIR, f"{team_name}.png")
    if os.path.exists(path):
        try:
            img = Image.open(path)
            img.thumbnail(size)
            return img
        except Exception:
            return None
    return None

def determine_position(row):
    """
    CSV 데이터를 기반으로 포지션을 결정하는 로직
    """
    try:
        stats = {
            "초공격형 레전드 슬러거": float(row.get('거래금액', 0)),
            "공격형 슈퍼소닉 리드오프": float(row.get('거래빈도', 0)),
            "밸런스형 육각형 올라운더": float(row.get('분산투자', 0)),
            "수비형 철벽 유격수": float(row.get('안정성_점수', 0)), 
            "안정형 정밀 타격 머신": float(row.get('해외비중', 0))  
        }
        best_pos = max(stats, key=stats.get)
        return best_pos
    except:
        return "밸런스형 육각형 올라운더" 

def validate_user(name, account):
    """
    customer_report_updated.csv 파일을 읽어 이름과 계좌번호가 일치하는지 확인
    """
    if not os.path.exists(CSV_FILE_PATH):
        st.error(f"❌ 데이터 파일({CSV_FILE_PATH})을 찾을 수 없습니다.")
        return False, None
    
    try:
        # 계좌번호를 문자열로 읽기
        df = pd.read_csv(CSV_FILE_PATH, dtype={'계좌번호': str})
        
        # 전처리
        df['이름'] = df['이름'].astype(str).str.strip()
        df['계좌번호'] = df['계좌번호'].astype(str).str.strip().str.replace('-', '')
        
        input_account = account.replace('-', '').strip()
        input_name = name.strip()
        
        # 일치하는 행 찾기
        user_row = df[(df['이름'] == input_name) & (df['계좌번호'] == input_account)]
        
        if not user_row.empty:
            return True, user_row.iloc[0]
        else:
            return False, None
            
    except Exception as e:
        st.error(f"데이터 확인 중 오류 발생: {e}")
        return False, None


# -----------------------------
# 🔥 Gemini AI 리포트 생성 함수
# -----------------------------
def generate_ai_report_gemini(team: str, position: str, number: str, name: str, stats_data) -> bytes:
    
    model_id = "gemini-3-pro-image-preview"
    
    # 1. 기본 스탯 추출
    p_avg = stats_data.get('AVG(수익률)', '???')
    p_ops = stats_data.get('OPS(활동성)', '???')
    p_era = stats_data.get('ERA(안정성)', '???')
    
    # 2. 레이더 차트 데이터
    radar_power = stats_data.get('거래금액', 50)
    radar_defense = stats_data.get('안정성_점수', 50)
    radar_contact = stats_data.get('분산투자', 50)
    radar_speed = stats_data.get('거래빈도', 50)
    radar_global = stats_data.get('해외비중', 50)

    # 3. Top 3 종목 및 수익률 데이터 추출
    stock1 = stats_data.get('종목1', '-')
    ret1 = stats_data.get('종목1 수익률', 0)
    stock2 = stats_data.get('종목2', '-')
    ret2 = stats_data.get('종목2 수익률', 0)
    stock3 = stats_data.get('종목3', '-')
    ret3 = stats_data.get('종목3 수익률', 0)
    
    # 프롬프트 구성 (투자 리포트 컨셉)
    prompt_text = f"""
    You are an expert UI/UX designer for fintech & sports infographics.
    
    [Task]
    Generate a **"2025 YIPP X KBO AI Investment Report"** image, optimized for Instagram Story (9:16 Aspect Ratio).
    
    [Design Style]
    - **Theme Color**: Use Mint Green (#008F53) as the primary accent color.
    - **Style**: Modern, clean, sleek, and data-driven infographic style.
    - **Layout**: Vertical layout (9:16).
    
    [Content to Visualize]
    1. **Header**: 
       - Title: "2025 YIPP AI Investment Report"
       - Subtitle: "Player Analysis: {name}"
    
    2. **Player Profile (Top Section)**:
       - Visual: A high-quality illustration of a baseball player wearing the **"{team}"** uniform.
       - Back View: Show the player's back with Name **"{name}"** and Number **"{number}"**.
       - Position Tag: Display **"{position}"** prominently.
    
    3. **Investment Radar (Middle Section)**:
       - Draw a pentagon radar chart with these 5 axes (Scale 0-100):
         - Trading Volume (거래금액): {radar_power}
         - Stability (안정성): {radar_defense}
         - Diversification (분산투자): {radar_contact}
         - Frequency (거래빈도): {radar_speed}
         - Global Share (해외비중): {radar_global}
    
    4. **Key Metrics (Baseball Stats)**:
       - AVG (Return): **{p_avg}**
       - OPS (Activity): **{p_ops}**
       - ERA (Stability): **{p_era}**
    
    5. **Top 3 Profit Stocks (Bottom Section - IMPORTANT)**:
       - Display a "Hall of Fame" or "Top Picks" list for this player.
       - 1st: **{stock1}** (+{ret1}%) -> Highlight this one (Gold/Best).
       - 2nd: **{stock2}** (+{ret2}%)
       - 3rd: **{stock3}** (+{ret3}%)
    
    [Output Requirement]
    - Output ONLY the generated image.
    - Aspect Ratio: 9:16 (Vertical).
    - Ensure Korean text (Names, Stocks) is legible and not broken.
    """

    parts = [types.Part.from_text(text=prompt_text)]
    ref_bytes = load_reference_bytes()
    
    if ref_bytes:
        parts.append(types.Part.from_bytes(data=ref_bytes, mime_type="image/png"))
    else:
        # 레퍼런스 이미지가 없어도 텍스트로 생성 시도
        pass 

    generate_content_config = types.GenerateContentConfig(
        response_modalities=["IMAGE"], 
        image_config=types.ImageConfig(image_size="1K")
    )

    try:
        response_stream = client.models.generate_content_stream(
            model=model_id,
            contents=[types.Content(role="user", parts=parts)],
            config=generate_content_config,
        )

        for chunk in response_stream:
            if chunk.candidates and chunk.candidates[0].content and chunk.candidates[0].content.parts:
                part = chunk.candidates[0].content.parts[0]
                if part.inline_data and part.inline_data.data:
                    raw_data = part.inline_data.data
                    try:
                        Image.open(BytesIO(raw_data)).verify()
                        return raw_data
                    except Exception:
                        pass
                    try:
                        decoded_data = base64.b64decode(raw_data)
                        Image.open(BytesIO(decoded_data)).verify()
                        return decoded_data
                    except Exception as e:
                        print(f"이미지 디코딩 실패: {e}")
                        continue

        raise Exception("모델 응답에서 유효한 이미지 데이터를 추출하지 못했습니다.")

    except Exception as e:
        st.error(f"❌ 이미지 생성 실패: {e}")
        # 실패 시 기본 이미지 반환
        fallback = Image.new('RGB', (540, 960), color=(0, 143, 83))
        buf = BytesIO()
        fallback.save(buf, format="PNG")
        return buf.getvalue()


# -----------------------------
# UI 단계별 함수
# -----------------------------

def step_login():
    st.header("① 내 선수 정보 입력")
    st.write("현재까지의 투자 기록을 바탕으로 내 AI 투자 리포트를 생성해보세요.")

    # CSS 적용 (민트색 버튼)
    st.markdown(f"""
    <style>
    div[data-testid="stButton"] button[kind="primary"] {{
        background-color: {THEME_COLOR} !important;
        border: none !important;
        color: white !important;
    }}
    div[data-testid="stButton"] button[kind="primary"]:hover {{
        background-color: #007A45 !important;
        opacity: 0.9;
    }}
    </style>
    """, unsafe_allow_html=True)

    # 1. 이름 입력
    name = st.text_input("이름", value=st.session_state["player_name"], placeholder="이름을 입력하세요")
    st.session_state["player_name"] = name

    # 2. 계좌번호 입력
    st.markdown("---")
    account = st.text_input("YIPP 계좌번호 (12자리)", value=st.session_state["account"], max_chars=12, placeholder="숫자만 입력해주세요")
    st.session_state["account"] = account

    # 유효성 검사
    is_valid_name = len(name.strip()) > 0
    is_valid_length = len(account) == 12
    is_numeric = account.isdigit()

    if account and (not is_numeric or not is_valid_length):
         st.markdown(f":red[❌ YIPP 계좌번호는 12자리입니다.]")

    st.markdown("<br>", unsafe_allow_html=True)

    # 리포트 생성 버튼
    if st.button("AI 투자리포트 생성하기", type="primary", use_container_width=True, disabled=not(is_valid_name and is_valid_length and is_numeric)):
        
        # CSV 조회 로직
        is_registered, row_data = validate_user(name, account)
        
        if is_registered:
            # 데이터 저장
            st.session_state["player_data"] = row_data
            
            # 팀 정보 가져오기
            fetched_team = row_data.get('팀', None)
            if fetched_team and str(fetched_team).lower() != 'nan' and str(fetched_team).strip() != "":
                st.session_state["team"] = str(fetched_team).strip()
            else:
                st.session_state["team"] = "SSG 랜더스" # 기본값
            
            st.session_state["number"] = account[-2:] 
            
            # 포지션 산정
            new_position = determine_position(row_data)
            st.session_state["position"] = new_position
            
            st.success(f"반갑습니다, {name}님! 투자 데이터를 분석 중입니다...")
            time.sleep(1) 
            go_next_step()
            st.rerun()
        else:
            st.error("등록되지 않은 선수입니다. YIPP 계좌 개설 후, 신인 선수 등록을 먼저 진행해주세요.")

def step_result():
    st.header("📊 AI 투자 리포트")

    data = st.session_state["player_data"]
    team = st.session_state["team"]
    num = st.session_state["number"]
    name = st.session_state["player_name"]
    pos = st.session_state["position"]

    # 버튼 스타일 복구
    st.markdown(f"""
    <style>
    div[data-testid="stButton"] button[kind="primary"] {{
        background-color: {THEME_COLOR} !important;
        color: white !important;
        border: none !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    st.subheader(f"{name}님의 2025 투자 분석")
    st.caption(f"소속: {team} | 포지션: {pos}")
    
    # 텍스트로 요약 정보 보여주기 (디버깅 겸용)
    with st.expander("📈 투자 기록 미리보기"):
        st.write(f"**수익률(AVG)**: {data.get('AVG(수익률)', '-')}")
        st.write(f"**TOP 1 종목**: {data.get('종목1', '-')} ({data.get('종목1 수익률', 0)}%)")
        st.write(f"**TOP 2 종목**: {data.get('종목2', '-')} ({data.get('종목2 수익률', 0)}%)")
        st.write(f"**TOP 3 종목**: {data.get('종목3', '-')} ({data.get('종목3 수익률', 0)}%)")

    status_container = st.empty()

    # 이미지 생성
    if st.session_state["report_image_bytes"] is None:
        status_container.info("🎨 AI가 고객님의 투자 성향과 수익률이 담긴 투자리포트를 생성 중입니다...")
        
        # Gemini 호출
        img_bytes = generate_ai_report_gemini(team, pos, num, name, data)
        st.session_state["report_image_bytes"] = img_bytes

    if st.session_state["report_image_bytes"]:
        status_container.info("✨ AI 투자리포트 생성 완료!")
        try:
            img = Image.open(BytesIO(st.session_state["report_image_bytes"]))
            st.image(img, use_container_width=True)
            
            st.download_button(
                label="📸 AI 투자리포트 공유하기",
                data=st.session_state["report_image_bytes"],
                file_name=f"yipp_report_{num}.png",
                mime="image/png",
                use_container_width=True,
                type="primary"
            )
        except Exception as e:
            st.error("이미지를 표시할 수 없습니다.")
            st.error(e)

    col1, col2 = st.columns(2)
    col1.button("뒤로", on_click=go_prev_step, type="secondary", use_container_width=True)
    col2.button("처음으로", on_click=reset_all, type="secondary", use_container_width=True)


# -----------------------------
# 네비게이션
# -----------------------------
def go_next_step():
    st.session_state["step"] += 1

def go_prev_step():
    st.session_state["step"] = max(1, st.session_state["step"] - 1)

def reset_all():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    init_session_state()


# -----------------------------
# 메인 실행 루프
# -----------------------------
def main():
    st.title("YIPP X KBO AI 투자리포트")
    
    step = st.session_state["step"]
    
    if step == 1:
        step_login()
    elif step == 2:
        step_result()

if __name__ == "__main__":
    main()