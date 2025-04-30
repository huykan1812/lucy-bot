
import os
from openai import OpenAI
from telegram import Update, File
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)
user_conversations = {}

lucy_intro = {
    "role": "system",
    "content": (
        "Bạn là Lucy, một thư ký riêng chuyên nghiệp, thân thiện, xưng 'Em' với người dùng là 'Anh'. "
        "Bạn hỗ trợ công việc, quản lý email, báo cáo và nhắc việc. "
        "Luôn giữ phong cách ngắn gọn, rõ ràng, thân thiện và hiệu quả."
    )
}

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_message = update.message.text

    if user_id not in user_conversations:
        user_conversations[user_id] = [lucy_intro]

    user_conversations[user_id].append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=user_conversations[user_id],
            max_tokens=1000,
            temperature=0.7,
        )
        reply = response.choices[0].message.content
        user_conversations[user_id].append({"role": "assistant", "content": reply})
    except Exception as e:
        reply = f"Lỗi: {e}"

    await update.message.reply_text(reply)

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    file_name = doc.file_name

    if not os.path.exists("downloads"):
        os.makedirs("downloads")

    new_file: File = await context.bot.get_file(doc.file_id)
    file_path = os.path.join("downloads", file_name)
    await new_file.download_to_drive(file_path)

    message = f"Em đã tải xong file: {file_name}."

    if file_name.endswith(('.docx', '.xlsx')):
        message += " Anh muốn em phân tích nội dung hay trích thông tin gì từ file này ạ?"
    else:
        message += " Hiện tại em chưa đọc được định dạng này, nhưng nếu cần em có thể xử lý sau."

    await update.message.reply_text(message)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(~filters.TEXT & ~filters.Document.ALL, handle_text))
    print("🤖 Lucy bot đang chạy trên Render!")
    app.run_polling()
