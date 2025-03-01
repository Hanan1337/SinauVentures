from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, ContextTypes
from config import TELEGRAM_TOKEN
from instagram import login_with_cookie, download_story, download_highlights, download_profile_pic, get_bio
import os
import logging

logging.basicConfig(
    filename='instagram_bot.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Fungsi untuk membuat menu tombol utama
def main_menu():
    keyboard = [
        [InlineKeyboardButton("Unduh Story", callback_data='story')],
        [InlineKeyboardButton("Unduh Highlights", callback_data='highlights')],
        [InlineKeyboardButton("Unduh Foto Profil", callback_data='profilepic')],
        [InlineKeyboardButton("Lihat Bio", callback_data='bio')]
    ]
    return InlineKeyboardMarkup(keyboard)

# Handler untuk perintah /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info(f"Perintah /start diterima dari user {update.effective_user.id}")
    await update.message.reply_text(
        "Selamat datang di Bot Instagram Downloader!\nPilih opsi di bawah ini:",
        reply_markup=main_menu()
    )
    logger.debug("Menu utama dikirim")

# Handler untuk tombol inline
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    action = query.data
    logger.info(f"Tombol {action} ditekan oleh user {query.from_user.id}")

    # Simpan action di context untuk digunakan di handler teks
    context.user_data['action'] = action
    await query.edit_message_text(f"Masukkan username Instagram untuk {action.replace('_', ' ')}:")

# Handler untuk menerima username dari pengguna
async def handle_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    username = update.message.text.strip()
    user_id = update.effective_user.id
    logger.info(f"Username {username} diterima dari user {user_id}")
    action = context.user_data.get('action')

    if not action:
        await update.message.reply_text("Silakan pilih tombol terlebih dahulu!", reply_markup=main_menu())
        return

    await update.message.reply_text(f"Memproses {action} untuk {username}...")

    try:
        if action == 'story':
            files = download_story(username)
            if not files:
                await update.message.reply_text("Tidak ada Story ditemukan atau akun privat.")
                return
            for file in files:
                logger.debug(f"Mengirim file Story: {file}")
                await context.bot.send_document(chat_id=update.effective_chat.id, document=open(file, 'rb'))
                os.remove(file)
                logger.debug(f"File Story dihapus: {file}")
            await update.message.reply_text("Selesai mengunduh Story!", reply_markup=main_menu())

        elif action == 'highlights':
            files = download_highlights(username)
            if not files:
                await update.message.reply_text("Tidak ada Highlights ditemukan atau akun privat.")
                return
            for file in files:
                logger.debug(f"Mengirim file Highlight: {file}")
                await context.bot.send_document(chat_id=update.effective_chat.id, document=open(file, 'rb'))
                os.remove(file)
                logger.debug(f"File Highlight dihapus: {file}")
            await update.message.reply_text("Selesai mengunduh Highlights!", reply_markup=main_menu())

        elif action == 'profilepic':
            file = download_profile_pic(username)
            if file:
                logger.debug(f"Mengirim foto profil: {file}")
                await context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(file, 'rb'))
                os.remove(file)
                logger.debug(f"File foto profil dihapus: {file}")
                await update.message.reply_text("Selesai mengunduh foto profil!", reply_markup=main_menu())
            else:
                await update.message.reply_text("Foto profil tidak ditemukan.", reply_markup=main_menu())

        elif action == 'bio':
            bio_info = get_bio(username)
            await update.message.reply_text(bio_info, reply_markup=main_menu())
            logger.info(f"Bio untuk {username} berhasil dikirim")

        logger.info(f"{action} untuk {username} selesai")
    except Exception as e:
        logger.error(f"Error saat memproses {action} untuk {username}: {str(e)}")
        await update.message.reply_text(f"Error: {str(e)}", reply_markup=main_menu())

    # Reset action setelah selesai
    context.user_data['action'] = None

def main():
    logger.info("Memulai bot...")
    try:
        login_with_cookie()
    except Exception as e:
        logger.critical(f"Tidak bisa menjalankan bot: {str(e)}")
        return

    try:
        logger.debug("Membangun aplikasi Telegram dengan token")
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        logger.info("Bot Telegram berhasil diinisialisasi")
    except Exception as e:
        logger.critical(f"Gagal menginisialisasi bot Telegram: {str(e)}")
        return

    # Handler untuk tombol dan teks
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_username))

    logger.info("Bot mulai berjalan")
    application.run_polling()

if __name__ == '__main__':
    main()
