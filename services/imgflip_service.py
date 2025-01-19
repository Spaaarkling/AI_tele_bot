import requests
import logging
import sys
from typing import Optional, Dict, List

# 로깅 설정
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

class ImgFlipService:
    def __init__(self, username: str, password: str):
        logger.debug(f"ImgFlip 서비스 초기화 시작 (username: {username})")
        self.base_url = "https://api.imgflip.com"
        self.username = username
        self.password = password
        
        if not username or not password:
            logger.error("ImgFlip 사용자 이름 또는 비밀번호가 제공되지 않았습니다.")
            raise ValueError("Username and password are required")
        
        logger.info("ImgFlip 서비스 초기화 완료")
        
    def get_meme_templates(self) -> List[Dict]:
        """Get popular meme templates from ImgFlip"""
        try:
            logger.debug("밈 템플릿 목록 가져오기 시도")
            response = requests.get(f"{self.base_url}/get_memes")
            if response.status_code == 200:
                data = response.json()
                logger.debug(f"밈 템플릿 {len(data.get('data', {}).get('memes', []))}개 가져옴")
                return data.get("data", {}).get("memes", [])
            logger.error(f"밈 템플릿 가져오기 실패: {response.status_code}")
            return []
        except Exception as e:
            logger.error(f"밈 템플릿 가져오기 중 오류 발생: {str(e)}")
            return []

    def create_meme(self, template_id: str, text0: str, text1: str = "") -> Optional[str]:
        """Create a meme using ImgFlip API"""
        try:
            logger.debug(f"밈 생성 시도 (template_id: {template_id}, text0: {text0}, text1: {text1})")
            url = f"{self.base_url}/caption_image"
            payload = {
                "template_id": template_id,
                "username": self.username,
                "password": self.password,
                "text0": text0,
                "text1": text1
            }
            
            response = requests.post(url, data=payload)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    meme_url = data.get("data", {}).get("url")
                    logger.debug(f"밈 생성 성공: {meme_url}")
                    return meme_url
                logger.error(f"ImgFlip API 오류: {data.get('error_message')}")
            else:
                logger.error(f"ImgFlip API 요청 실패: {response.status_code}")
            return None
        except Exception as e:
            logger.error(f"밈 생성 중 오류 발생: {str(e)}")
            return None

    def find_template_by_keyword(self, keyword: str) -> Optional[Dict]:
        """Find a meme template that matches the given keyword"""
        try:
            logger.debug(f"키워드로 템플릿 검색: {keyword}")
            templates = self.get_meme_templates()
            keyword = keyword.lower()
            
            # First try exact match
            for template in templates:
                if keyword in template.get("name", "").lower():
                    logger.debug(f"정확한 매치 찾음: {template.get('name')}")
                    return template
                    
            # If no exact match, try partial match
            for template in templates:
                name = template.get("name", "").lower()
                if any(word in name for word in keyword.split()):
                    logger.debug(f"부분 매치 찾음: {template.get('name')}")
                    return template
                    
            # Return most popular template if no match found
            if templates:
                logger.debug("매치 없음, 가장 인기있는 템플릿 반환")
                return templates[0]
            
            logger.warning("사용 가능한 템플릿 없음")
            return None
        except Exception as e:
            logger.error(f"템플릿 검색 중 오류 발생: {str(e)}")
            return None
