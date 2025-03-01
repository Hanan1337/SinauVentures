import instaloader
import os
import json
import random
import time
import logging
from config import INSTAGRAM_COOKIE

logging.basicConfig(
    filename='instagram_bot.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_user_agents():
    try:
        with open('user_agents.json', 'r') as f:
            user_agents = json.load(f)
        logger.debug(f"User-Agents dimuat: {len(user_agents)} entri")
        return user_agents
    except Exception as e:
        logger.error(f"Gagal memuat user_agents.json: {str(e)}")
        raise

def get_random_user_agent():
    user_agents = load_user_agents()
    user_agent = random.choice(user_agents)
    logger.debug(f"User-Agent dipilih: {user_agent}")
    return user_agent

def add_fixed_delay():
    delay = 5
    logger.debug(f"Menambahkan delay {delay} detik sebelum request")
    time.sleep(delay)

L = instaloader.Instaloader(user_agent=get_random_user_agent())
logger.debug("Instaloader diinisialisasi dengan User-Agent acak")

def login_with_cookie():
    try:
        add_fixed_delay()
        logger.info("Mencoba login dengan cookie")
        logger.debug(f"Cookies yang akan digunakan: {INSTAGRAM_COOKIE}")
        for key, value in INSTAGRAM_COOKIE.items():
            L.context._session.cookies.set(key, value)
            logger.debug(f"Cookie ditambahkan: {key}={value[:10]}... (ditruncate untuk keamanan)")
        L.context.is_logged_in = True
        username = L.context.username
        logger.info(f"Berhasil login sebagai {username} dengan cookie")
        logger.debug("Sesi login telah diatur")
    except Exception as e:
        logger.error(f"Gagal login: {str(e)}")
        raise

def download_story(username):
    try:
        add_fixed_delay()
        L.user_agent = get_random_user_agent()
        logger.info(f"Mengunduh Story untuk {username}")
        logger.debug(f"Mengambil profil untuk {username}")
        profile = instaloader.Profile.from_username(L.context, username)
        logger.debug(f"Profile ID: {profile.userid}")
        stories = []
        for story in L.get_stories([profile.userid]):
            logger.debug(f"Story ditemukan: {story}")
            for item in story.get_items():
                logger.debug(f"Mengunduh item Story: {item}")
                L.download_storyitem(item, target=f"{username}_story")
                for file in os.listdir(f"{username}_story"):
                    full_path = f"{username}_story/{file}"
                    stories.append(full_path)
                    logger.debug(f"Story ditambahkan ke daftar: {full_path}")
        logger.info(f"Selesai mengunduh Story untuk {username}, total: {len(stories)} file")
        return stories
    except Exception as e:
        logger.error(f"Error saat mengunduh Story untuk {username}: {str(e)}")
        raise

def download_highlights(username):
    try:
        add_fixed_delay()
        L.user_agent = get_random_user_agent()
        logger.info(f"Mengunduh Highlights untuk {username}")
        logger.debug(f"Mengambil profil untuk {username}")
        profile = instaloader.Profile.from_username(L.context, username)
        logger.debug(f"Profile ID: {profile.userid}")
        highlights = []
        for highlight in L.get_highlights(profile.userid):
            logger.debug(f"Highlight ditemukan: {highlight}")
            for item in highlight.get_items():
                logger.debug(f"Mengunduh item Highlight: {item}")
                L.download_storyitem(item, target=f"{username}_highlights")
                for file in os.listdir(f"{username}_highlights"):
                    full_path = f"{username}_highlights/{file}"
                    highlights.append(full_path)
                    logger.debug(f"Highlight ditambahkan ke daftar: {full_path}")
        logger.info(f"Selesai mengunduh Highlights untuk {username}, total: {len(highlights)} file")
        return highlights
    except Exception as e:
        logger.error(f"Error saat mengunduh Highlights untuk {username}: {str(e)}")
        raise

def download_profile_pic(username):
    try:
        add_fixed_delay()
        L.user_agent = get_random_user_agent()
        logger.info(f"Mengunduh foto profil untuk {username}")
        logger.debug(f"Mengunduh profil untuk {username} dengan profile_pic_only=True")
        L.download_profile(username, profile_pic_only=True)
        for file in os.listdir(username):
            if file.endswith(".jpg") or file.endswith(".png"):
                full_path = f"{username}/{file}"
                logger.info(f"Foto profil ditemukan: {full_path}")
                return full_path
        logger.warning(f"Tidak ada foto profil ditemukan untuk {username}")
        return None
    except Exception as e:
        logger.error(f"Error saat mengunduh foto profil untuk {username}: {str(e)}")
        raise

def get_bio(username):
    try:
        add_fixed_delay()
        L.user_agent = get_random_user_agent()
        logger.info(f"Mengambil bio untuk {username}")
        logger.debug(f"Mengambil profil untuk {username}")
        profile = instaloader.Profile.from_username(L.context, username)
        logger.debug(f"Profile ID: {profile.userid}")
        bio_info = (
            f"Username: {profile.username}\n"
            f"Nama: {profile.full_name}\n"
            f"Bio: {profile.biography}\n"
            f"Followers: {profile.followers}\n"
            f"Following: {profile.followees}"
        )
        logger.info(f"Bio berhasil diambil untuk {username}")
        logger.debug(f"Isi bio: {bio_info}")
        return bio_info
    except Exception as e:
        logger.error(f"Error saat mengambil bio untuk {username}: {str(e)}")
        raise
