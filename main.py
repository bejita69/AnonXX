import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Mengambil token secara aman dari Environment Variable
TOKEN = os.getenv("TOKEN")

waiting_queue = []
active_pairs = {} # format: {user_id: partner_id}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Selamat datang di Anonymous XNXX!\n\n"
        "Gunakan perintah:\n"
        "/search - Cari pasangan obrolan\n"
        "/stop - Hentikan obrolan saat ini"
    )

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id in active_pairs:
        await update.message.reply_text("Anda sedang dalam obrolan! Ketik /stop dulu untuk keluar.")
        return
        
    if user_id in waiting_queue:
        await update.message.reply_text("Sedang mencari pasangan... Mohon tunggu.")
        return

    if waiting_queue:
        # Hubungkan pengguna dengan orang pertama di antrean
        partner_id = waiting_queue.pop(0)
        active_pairs[user_id] = partner_id
        active_pairs[partner_id] = user_id
        
        await update.message.reply_text("Pasangan ditemukan! Selamat mengobrol. (Ketik /stop untuk mengakhiri)")
        await context.bot.send_message(chat_id=partner_id, text="Pasangan ditemukan! Selamat mengobrol. (Ketik /stop untuk mengakhiri)")
    else:
        waiting_queue.append(user_id)
        await update.message.reply_text("Mencari pasangan obrolan...")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id in waiting_queue:
        waiting_queue.remove(user_id)
        await update.message.reply_text("Pencarian dibatalkan.")
        return

    if user_id in active_pairs:
        partner_id = active_pairs.pop(user_id)
        active_pairs.pop(partner_id, None)
        
        await update.message.reply_text("Obrolan dihentikan. Ketik /search untuk mencari pasangan baru.")
        await context.bot.send_message(chat_id=partner_id, text="Pasangan Anda telah menghentikan obrolan. Ketik /search untuk mencari pasangan baru.")
    else:
        await update.message.reply_text("Anda tidak sedang berada dalam obrolan.")

async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id in active_pairs:
        partner_id = active_pairs[user_id]
        # Teruskan pesan/media dari pengguna ke pasangannya
        await context.bot.copy_message(
            chat_id=partner_id,
            from_chat_id=update.effective_chat.id,
            message_id=update.message.message_id
        )

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("search", search))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, forward_message))
    
    print("Bot Anonymous Chat sedang berjalan...")
    app.run_polling()
