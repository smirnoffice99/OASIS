"""
launcher.py — OASIS 실행 진입점 (PyInstaller 빌드용)

PyInstaller로 빌드 시 이 파일이 main entry point가 된다.
FastAPI 서버를 백그라운드에서 시작하고 브라우저를 자동으로 연다.
"""

import sys
import os
import threading
import time
import webbrowser
from pathlib import Path

# ---------------------------------------------------------------------------
# 경로 설정: 실행파일(.exe) 기준으로 데이터 디렉토리 결정
# ---------------------------------------------------------------------------

if getattr(sys, "frozen", False):
    # PyInstaller 번들 실행 시
    BASE_DIR = Path(sys.executable).parent
    BUNDLE_DIR = Path(sys._MEIPASS)  # 번들 내부 임시 디렉토리
else:
    # 일반 Python 실행 시
    BASE_DIR = Path(__file__).parent
    BUNDLE_DIR = BASE_DIR

# 사용자 데이터 디렉토리 (exe 옆에 생성)
DATA_DIR = BASE_DIR / "oasis_data"
DATA_DIR.mkdir(exist_ok=True)
(DATA_DIR / "cases").mkdir(exist_ok=True)
(DATA_DIR / "samples").mkdir(exist_ok=True)
(DATA_DIR / "prompts").mkdir(exist_ok=True)

# 번들 내 prompts를 데이터 디렉토리로 복사 (최초 1회)
import shutil

for src in (BUNDLE_DIR / "prompts").glob("*.txt"):
    dst = DATA_DIR / "prompts" / src.name
    if not dst.exists():
        shutil.copy2(src, dst)

# .env 파일 경로
ENV_PATH = BASE_DIR / ".env"

# ---------------------------------------------------------------------------
# 환경변수 로드
# ---------------------------------------------------------------------------

from dotenv import load_dotenv
load_dotenv(ENV_PATH)

# sys.path에 번들 디렉토리 추가
sys.path.insert(0, str(BUNDLE_DIR))

# ---------------------------------------------------------------------------
# 포트 설정
# ---------------------------------------------------------------------------

PORT = 8000
HOST = "127.0.0.1"
URL = f"http://{HOST}:{PORT}"


def find_free_port(start: int = 8000) -> int:
    import socket
    for port in range(start, start + 100):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((HOST, port))
                return port
            except OSError:
                continue
    return start


# ---------------------------------------------------------------------------
# 서버 실행
# ---------------------------------------------------------------------------

def run_server(port: int):
    import uvicorn

    # CASES_ROOT / SAMPLES_ROOT 환경변수로 덮어쓰기
    os.environ["OASIS_DATA_DIR"] = str(DATA_DIR)

    # PyInstaller console=False 환경에서 stdout/stderr가 None이면
    # uvicorn 로깅이 실패하므로 null stream으로 대체한다
    import io
    if sys.stdout is None:
        sys.stdout = io.StringIO()
    if sys.stderr is None:
        sys.stderr = io.StringIO()

    uvicorn.run(
        "web.app:app",
        host=HOST,
        port=port,
        log_config=None,  # uvicorn 기본 로깅 설정 비활성화
    )


def wait_and_open_browser(port: int):
    import urllib.request
    url = f"http://{HOST}:{port}"
    for _ in range(30):
        try:
            urllib.request.urlopen(url, timeout=1)
            webbrowser.open(url)
            return
        except Exception:
            time.sleep(0.5)


# ---------------------------------------------------------------------------
# 시작
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = find_free_port(PORT)

    # 브라우저 열기 (서버 준비되면 자동 오픈)
    browser_thread = threading.Thread(
        target=wait_and_open_browser, args=(port,), daemon=True
    )
    browser_thread.start()

    print(f"OASIS 시작 중... http://{HOST}:{port}")
    run_server(port)
