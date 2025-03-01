from dotenv import load_dotenv
import os
import logging

logging.basicConfig(
    filename='instagram_bot.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.debug("Memulai pemuatan konfigurasi dari .env")
load_dotenv()

try:
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    logger.debug(f"TELEGRAM_TOKEN: {TELEGRAM_TOKEN[:5]}... (ditruncate untuk keamanan)")

    INSTAGRAM_COOKIE = {
        "sessionid": os.getenv("SESSIONID"),
        "csrftoken": os.getenv("CSRFTOKEN"),
        "rur": os.getenv("RUR"),
        "mid": os.getenv("MID"),
        "ds_user_id": os.getenv("DS_USER_ID")
    }
    logger.debug(f"INSTAGRAM_COOKIE keys: {list(INSTAGRAM_COOKIE.keys())}")
    logger.debug(f"Cookie values (truncated): { {k: v[:10] + '...' if v else None for k, v in INSTAGRAM_COOKIE.items()} }")
    logger.info("Konfigurasi dari .env berhasil dimuat")
except Exception as e:
    logger.error(f"Gagal memuat konfigurasi dari .env: {str(e)}")
    raise
