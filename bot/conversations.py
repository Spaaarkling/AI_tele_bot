"""
대화 흐름 관리 모듈

이 모듈은 텔레그램 봇의 대화 흐름을 관리합니다.
사용자와의 상호작용을 단계별로 처리하고, 각 단계에서 적절한 응답을 제공합니다.
"""

import logging
import sys
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters
)
from services.imgflip_service import ImgFlipService
import os

# 로깅 설정
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# ImgFlip 서비스 인스턴스
def initialize_imgflip_service():
    try:
        imgflip_username = os.getenv('IMGFLIP_USERNAME')
        imgflip_password = os.getenv('IMGFLIP_PASSWORD')
        
        logger.debug(f"ImgFlip 사용자 이름: {imgflip_username}")
        logger.debug(f"ImgFlip 비밀번호가 설정되었나요? {'예' if imgflip_password else '아니오'}")
        
        if not imgflip_username or not imgflip_password:
            raise ValueError("IMGFLIP_USERNAME 또는 IMGFLIP_PASSWORD가 설정되지 않았습니다.")
        
        imgflip_service = ImgFlipService(
            username=imgflip_username,
            password=imgflip_password
        )
        logger.info("ImgFlip 서비스 초기화 성공")
        return imgflip_service
    except Exception as e:
        logger.error(f"ImgFlip 서비스 초기화 중 오류 발생: {str(e)}")
        return None

imgflip_service = initialize_imgflip_service()

# 대화 상태 정의
(WAITING_START,
 COIN_INPUT,      # 코인명 입력
 EMOTION_SELECT,  # 감정 선택
 CHARACTER_SELECT,# 캐릭터 선택
 LANGUAGE_SELECT, # 문구 언어 선택
 GENERATING,      # 밈 생성 중
 HELP_MENU) = range(7)

# 키보드 메뉴 정의
START_KEYBOARD = [
    ['🎨 코인 밈 만들기'],
    ['❓ 도움말']
]

EMOTION_KEYBOARD = [
    ['🚀 긍정적', '😢 부정적']
]

CHARACTER_KEYBOARD = [
    ['🐸 페페', '🚀 일론머스크'],
    ['👨‍💼 트럼프', '🐕 도지'],
    ['🎮 워작']
]

LANGUAGE_KEYBOARD = [
    ['🇰🇷 한글', '🇺🇸 영어']
]

# 캐릭터별 템플릿 ID 매핑
CHARACTER_TEMPLATES = {
    '🐸 페페': {
        '긍정적': '148909805',  # 행복한 페페
        '부정적': '114485854'   # 슬픈 페페
    },
    '🚀 일론머스크': {
        '긍정적': '101470',     # 웃는 일론머스크
        '부정적': '119139145'   # 실망한 일론머스크
    },
    '👨‍💼 트럼프': {
        '긍정적': '91545132',   # 웃는 트럼프
        '부정적': '91545132'    # 화난 트럼프
    },
    '🐕 도지': {
        '긍정적': '8072285',    # 행복한 도지
        '부정적': '247375501'   # 슬픈 도지
    },
    '🎮 워작': {
        '긍정적': '61579',      # 웃는 워작
        '부정적': '61579'       # 슬픈 워작
    }
}

# 문구 템플릿
PHRASES = {
    '한글': {
        '긍정적': [
            '가즈아!!!',
            '개이득',
            '존버는 승리한다',
            '달나라 가즈아',
            '홀더의 승리'
        ],
        '부정적': [
            '망했다',
            '손절각',
            '물렸다',
            '존버 실패',
            '거래소 멈춤'
        ]
    },
    '영어': {
        '긍정적': [
            'LFG! 🚀',
            'WAGMI',
            'Bullish!',
            'To The Moon!',
            'Diamond Hands 💎'
        ],
        '부정적': [
            'NGMI',
            'Bearish',
            'Panic Sell',
            'RIP',
            'Paper Hands 📄'
        ]
    }
}

async def start_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """시작 명령어 처리"""
    await update.message.reply_text(
        "안녕하세요! 🎨 코인 밈 생성 봇입니다.\n\n"
        "코인 관련 재미있는 밈을 만들어드립니다!\n"
        "시작하려면 '🎨 코인 밈 만들기' 버튼을 눌러주세요.",
        reply_markup=ReplyKeyboardMarkup(START_KEYBOARD, resize_keyboard=True)
    )
    return WAITING_START

async def handle_start_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """시작 응답 처리"""
    text = update.message.text
    
    if text == '🎨 코인 밈 만들기':
        await update.message.reply_text(
            "어떤 코인의 밈을 만들까요? 😊\n"
            "코인의 심볼을 입력해주세요.\n\n"
            "예시: BTC, ETH, DOGE"
        )
        return COIN_INPUT
    elif text == '❓ 도움말':
        return await help_command(update, context)
    else:
        await update.message.reply_text("메뉴에서 옵션을 선택해주세요.")
        return WAITING_START

async def handle_coin_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """코인명 입력 처리"""
    coin = update.message.text.upper()
    context.user_data['coin'] = coin
    
    await update.message.reply_text(
        f"{coin}에 대한 감정을 선택해주세요!",
        reply_markup=ReplyKeyboardMarkup(EMOTION_KEYBOARD, resize_keyboard=True)
    )
    return EMOTION_SELECT

async def handle_emotion_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """감정 선택 처리"""
    emotion = '긍정적' if '긍정적' in update.message.text else '부정적'
    context.user_data['emotion'] = emotion
    
    await update.message.reply_text(
        "밈에 사용할 캐릭터를 선택해주세요!",
        reply_markup=ReplyKeyboardMarkup(CHARACTER_KEYBOARD, resize_keyboard=True)
    )
    return CHARACTER_SELECT

async def handle_character_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """캐릭터 선택 처리"""
    character = update.message.text
    context.user_data['character'] = character
    
    await update.message.reply_text(
        "문구의 언어를 선택해주세요!",
        reply_markup=ReplyKeyboardMarkup(LANGUAGE_KEYBOARD, resize_keyboard=True)
    )
    return LANGUAGE_SELECT

async def handle_language_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """언어 선택 및 밈 생성"""
    language = '한글' if '한글' in update.message.text else '영어'
    context.user_data['language'] = language
    
    # 생성 중 메시지 전송
    processing_message = await update.message.reply_text(
        "🎨 밈을 생성하고 있습니다...\n"
        "잠시만 기다려주세요!"
    )
    
    try:
        if not imgflip_service:
            raise ValueError("ImgFlip 서비스가 초기화되지 않았습니다.")
            
        # 저장된 데이터 가져오기
        coin = context.user_data['coin']
        emotion = context.user_data['emotion']
        character = context.user_data['character']
        
        # 템플릿 ID 가져오기
        template_id = CHARACTER_TEMPLATES[character][emotion]
        
        # 랜덤 문구 선택
        import random
        phrases = PHRASES[language][emotion]
        text_top = f"${coin}"
        text_bottom = random.choice(phrases)
        
        logger.debug(f"밈 생성 시도: template_id={template_id}, text_top={text_top}, text_bottom={text_bottom}")
        
        # 밈 생성
        meme_url = imgflip_service.create_meme(
            template_id,
            text_top,
            text_bottom
        )
        
        if not meme_url:
            raise ValueError("밈 URL을 생성하지 못했습니다.")
        
        logger.debug(f"생성된 밈 URL: {meme_url}")
        
        # 결과 전송
        await processing_message.delete()
        await update.message.reply_photo(
            photo=meme_url,
            caption=f"🎨 {coin} 밈이 생성되었습니다!\n\n"
                    f"캐릭터: {character}\n"
                    f"감정: {'🚀 긍정적' if emotion == '긍정적' else '😢 부정적'}\n\n"
                    f"다른 밈을 만들고 싶으시다면 '🎨 코인 밈 만들기'를 눌러주세요!",
            reply_markup=ReplyKeyboardMarkup(START_KEYBOARD, resize_keyboard=True)
        )
        
    except Exception as e:
        logger.error(f"밈 생성 중 오류 발생: {str(e)}")
        await processing_message.edit_text(
            "😅 죄송합니다. 오류가 발생했어요.\n"
            "다시 시도해주세요!"
        )
    
    return WAITING_START

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """도움말 명령어 처리"""
    help_text = (
        "🎨 코인 밈 생성 봇 사용법:\n\n"
        "1. '코인 밈 만들기' 버튼을 클릭하세요\n"
        "2. 코인 심볼을 입력하세요 (예: BTC)\n"
        "3. 감정을 선택하세요 (긍정/부정)\n"
        "4. 캐릭터를 선택하세요\n"
        "5. 문구 언어를 선택하세요\n\n"
        "명령어:\n"
        "/start - 시작하기\n"
        "/cancel - 취소하기\n"
        "/help - 도움말 보기"
    )
    await update.message.reply_text(
        help_text,
        reply_markup=ReplyKeyboardMarkup(START_KEYBOARD, resize_keyboard=True)
    )
    return WAITING_START

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """취소 명령어 처리"""
    await update.message.reply_text(
        "🛑 밈 생성이 취소되었습니다. 새로 시작하려면 /start 를 입력하세요.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

# 대화 핸들러 정의
analysis_conversation = ConversationHandler(
    entry_points=[
        CommandHandler("start", start_conversation),
        CommandHandler("help", help_command),
        CommandHandler("cancel", cancel)
    ],
    
    states={
        WAITING_START: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_start_response)
        ],
        COIN_INPUT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_coin_input)
        ],
        EMOTION_SELECT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_emotion_select)
        ],
        CHARACTER_SELECT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_character_select)
        ],
        LANGUAGE_SELECT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_language_select)
        ],
        HELP_MENU: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, help_command)
        ]
    },
    
    fallbacks=[
        CommandHandler("start", start_conversation),
        CommandHandler("help", help_command),
        CommandHandler("cancel", cancel)
    ]
)
