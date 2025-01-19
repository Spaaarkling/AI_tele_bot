import os
import sys
import logging
from telegram import Update
from telegram.ext import Application
from dotenv import load_dotenv

# 환경 변수 로드 (가장 먼저 실행)
load_dotenv(override=True)

# 로깅 설정
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    force=True,
    stream=sys.stdout  # 표준 출력으로 로그 전송
)

logger = logging.getLogger(__name__)

# 환경 변수 확인 및 로깅
def check_environment():
    print("\n=== 환경 변수 확인 ===")
    
    token = os.getenv('TELEGRAM_TOKEN')
    imgflip_username = os.getenv('IMGFLIP_USERNAME')
    imgflip_password = os.getenv('IMGFLIP_PASSWORD')
    
    print(f"텔레그램 토큰: {token[:10]}...")
    print(f"ImgFlip 사용자 이름: {imgflip_username}")
    print(f"ImgFlip 비밀번호 설정됨: {'예' if imgflip_password else '아니오'}")
    print("=====================\n")
    
    if not all([token, imgflip_username, imgflip_password]):
        missing = []
        if not token: missing.append('TELEGRAM_TOKEN')
        if not imgflip_username: missing.append('IMGFLIP_USERNAME')
        if not imgflip_password: missing.append('IMGFLIP_PASSWORD')
        print(f"오류: 필수 환경 변수가 설정되지 않았습니다: {', '.join(missing)}")
        return False
    return True

# 봇 핸들러 임포트 (환경 변수 로드 후에 임포트)
from bot.conversations import analysis_conversation

def main():
    """봇 실행"""
    # 환경 변수 확인
    if not check_environment():
        print("환경 변수 설정이 올바르지 않아 봇을 시작할 수 없습니다.")
        return
    
    # 봇 생성
    token = os.getenv('TELEGRAM_TOKEN')
    application = Application.builder().token(token).build()
    
    # 대화 핸들러 등록
    application.add_handler(analysis_conversation)
    
    # 봇 실행
    print("봇이 시작되었습니다. Ctrl+C를 눌러 종료할 수 있습니다.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
