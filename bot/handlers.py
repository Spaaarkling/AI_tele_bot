from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """시작 명령어 처리"""
    await update.message.reply_text(
        "안녕하세요! 🎨 코인 밈 생성 봇입니다.\n\n"
        "코인 관련 재미있는 밈을 만들어드립니다!\n"
        "다양한 캐릭터와 문구로 당신만의 코인 밈을 만들어보세요.",
        reply_markup=ReplyKeyboardMarkup([['🎨 코인 밈 만들기'], ['❓ 도움말']], resize_keyboard=True)
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """도움말 명령어 처리"""
    help_text = (
        "🎨 코인 밈 생성 봇 사용법:\n\n"
        "1. '코인 밈 만들기' 버튼을 클릭하세요\n"
        "2. 코인 심볼을 입력하세요 (예: BTC)\n"
        "3. 감정을 선택하세요 (긍정/부정)\n"
        "4. 캐릭터를 선택하세요\n"
        "   - 페페 (긍정/부정 버전)\n"
        "   - 일론머스크 (긍정/부정 버전)\n"
        "   - 트럼프 (긍정/부정 버전)\n"
        "   - 도지 (긍정/부정 버전)\n"
        "   - 워작 (긍정/부정 버전)\n"
        "5. 문구 언어를 선택하세요\n"
        "   - 한글 (가즈아, 개이득, 존버 등)\n"
        "   - 영어 (LFG, WAGMI, Bullish 등)\n\n"
        "명령어:\n"
        "/start - 시작하기\n"
        "/cancel - 취소하기\n"
        "/help - 도움말 보기"
    )
    await update.message.reply_text(help_text)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """에러 처리"""
    print(f'Update {update} caused error {context.error}')
