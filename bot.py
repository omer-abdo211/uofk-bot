import logging
import sqlite3
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# إعداد السجل
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# إعداد قاعدة البيانات
def init_db():
    conn = sqlite3.connect("uofk_bot.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            specialty TEXT,
            semester TEXT,
            subject TEXT,
            section TEXT,
            file_id TEXT,
            file_name TEXT
        )
    """
    )
    conn.commit()
    conn.close()

init_db()

SPECIALTIES = {
    "control": "المستوى الأول - تحكم",
    "power": "المستوى الأول - قدرة",
    "med": "المستوى الأول - طبية",
    "networks": "المستوى الأول - شبكات",
}

SECTIONS = {
    "lectures": "📖 المحاضرات والفيديوهات",
    "sheets": "📝 الشيتات",
    "summaries": "📊 الملخصات",
    "exams": "🎯 الامتحانات السابقة",
}

CURRICULUM = {
    "control": {
        "sem1": [
            "EE 111 - لغة إنجليزية 1",
            "EE 112 - الحسبان",
            "EE 113 - الفيزياء",
            "EE 114 - مقدمة الحاسوب",
            "EE 115 - أعمال الورش 1",
            "EE 116 - رسم هندسي",
            "EE 127 - ميكانيكا الهندسة (ديناميكا واستاتيكا)",
        ],
        "sem2": [
            "EE 121 - لغة إنجليزية 2",
            "EE 122 - أخلاقيات المهنة",
            "EE 123 - الجبر الخطي والمعادلات التفاضلية",
            "EE 124 - برمجة الحاسوب",
            "EE 125 - أساسيات الهندسة الكهربائية",
            "EE 126 - أساسيات الالكترونيات التناظرية",
        ],
    },
    "power": {
        "sem1": [
            "ENG111 - لغة إنجليزية 1",
            "MAT112 - الحسبان",
            "PHY113 - الفيزياء",
            "COM114 - مقدمة الحاسوب",
            "WOK115 - أعمال الورش 1",
            "DRW116 - رسم هندسي",
            "ENGM127 - ميكانيكا الهندسة (ديناميكا واستاتيكا)",
        ],
        "sem2": [
            "ENG121 - لغة إنجليزية 2",
            "ETH122 - أخلاقيات المهنة",
            "MAT123 - الجبر الخطي والمعادلات التفاضلية",
            "COM124 - برمجة الحاسوب",
            "EEG125 - أساسيات الهندسة الكهربائية",
            "EEG126 - أساسيات الالكترونيات التناظرية",
        ],
    },
    "med": {
        "sem1": [
            "ENG111 - لغة إنجليزية 1",
            "MAT112 - الحسبان",
            "PHY113 - الفيزياء",
            "COM114 - مقدمة الحاسوب",
            "WOK115 - أعمال الورش 1",
            "DRW116 - رسم هندسي",
            "ENGM127 - ميكانيكا الهندسة (ديناميكا واستاتيكا)",
        ],
        "sem2": [
            "ENG121 - لغة إنجليزية 2",
            "ETH122 - أخلاقيات المهنة",
            "MAT123 - الجبر الخطي والمعادلات التفاضلية",
            "COM124 - برمجة الحاسوب",
            "EEG125 - أساسيات الهندسة الكهربائية",
            "EEG126 - أساسيات الالكترونيات التناظرية",
            "CHM128 - الكيمياء العامة",
        ],
    },
    "networks": {
        "sem1": [
            "NT111 - لغة إنجليزية 1",
            "NT112 - الحسبان",
            "NT113 - الفيزياء",
            "NT114 - مقدمة الحاسوب",
            "NT115 - أعمال الورش 1",
            "ميكانيكا الهندسة (ديناميكا واستاتيكا)",
        ],
        "sem2": [
            "NT121 - لغة إنجليزية 2",
            "NT122 - أخلاقيات المهنة",
            "NT123 - الجبر الخطي والمعادلات التفاضلية",
            "NT124 - برمجة الحاسوب",
            "NT125 - أساسيات الهندسة الكهربائية",
            "NT126 - أساسيات تصميم النظم الرقمية",
        ],
    },
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for code, name in SPECIALTIES.items():
        keyboard.append([InlineKeyboardButton(name, callback_data=f"spec_{code}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_text = (
        "مرحباً بك في بوت أرشيف هندسة جامعة الخرطوم.\n\n"
        "يرجى اختيار التخصص الأكاديمي:"
    )

    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    elif update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(welcome_text, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("spec_"):
        spec_code = data.split("_")[1]
        context.user_data["current_spec"] = spec_code
        spec_name = SPECIALTIES.get(spec_code, "التخصص")

        keyboard = [
            [InlineKeyboardButton("📚 السمستر الأول", callback_data=f"sem_{spec_code}_sem1")],
            [InlineKeyboardButton("📚 السمستر الثاني", callback_data=f"sem_{spec_code}_sem2")],
            [InlineKeyboardButton("🔙 رجوع للتخصصات", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text=f"التخصص: **{spec_name}**\nاختر السمستر الدراسي:",
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )

    elif data.startswith("sem_"):
        parts = data.split("_")
        spec_code = parts[1]
        sem_code = parts[2]
        context.user_data["current_sem"] = sem_code
        
        spec_name = SPECIALTIES.get(spec_code, "التخصص")
        sem_name = "السمستر الأول" if sem_code == "sem1" else "السمستر الثاني"

        subjects = CURRICULUM.get(spec_code, {}).get(sem_code, [])
        keyboard = []
        for idx, subj in enumerate(subjects):
            keyboard.append([InlineKeyboardButton(subj, callback_data=f"subj_{spec_code}_{sem_code}_{idx}")])

        keyboard.append([InlineKeyboardButton("🔙 رجوع للسمسترات", callback_data=f"spec_{spec_code}")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text=f"التخصص: **{spec_name}** ({sem_name})\nاختر المادة المطلوبة:",
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )

    elif data.startswith("subj_"):
        parts = data.split("_")
        spec_code = parts[1]
        sem_code = parts[2]
        subj_idx = int(parts[3])
        
        subjects = CURRICULUM.get(spec_code, {}).get(sem_code, [])
        subj_name = subjects[subj_idx]
        context.user_data["current_subj"] = subj_name

        keyboard = []
        for sec_code, sec_name in SECTIONS.items():
            keyboard.append([InlineKeyboardButton(sec_name, callback_data=f"sec_{sec_code}")])

        keyboard.append([InlineKeyboardButton("🔙 رجوع للمواد", callback_data=f"sem_{spec_code}_{sem_code}")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text=f"المادة: **{subj_name}**\nاختر القسم المطلوب:",
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )

    elif data.startswith("sec_"):
        sec_code = data.split("_")[1]
        context.user_data["current_sec"] = sec_code
        
        spec_code = context.user_data.get("current_spec")
        sem_code = context.user_data.get("current_sem")
        subj_name = context.user_data.get("current_subj")
        sec_name = SECTIONS.get(sec_code, "القسم")

        # حفظ الحالة لكي يعرف البوت أين سيرسل المستخدم الملف القادم
        context.user_data["uploading"] = True

        conn = sqlite3.connect("uofk_bot.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT file_id, file_name FROM files WHERE specialty = ? AND semester = ? AND subject = ? AND section = ?",
            (spec_code, sem_code, subj_name, sec_code)
        )
        files = cursor.fetchall()
        conn.close()

        text = f"المادة: **{subj_name}**\nالقسم: **{sec_name}**\n\n"
        if files:
            text += "📁 الملفات المتوفرة:\n"
            for f_id, f_name in files:
                text += f"- {f_name or 'ملف'}\n"
        else:
            text += "*(لا توجد ملفات مرفوعة في هذا القسم حتى الآن)*\n\n"

        text += "📤 **أرسل الملف الآن (ملف PDF، صورة، أو مستند) ليتم حفظه مباشرة في هذا القسم!**"

        keyboard = [[InlineKeyboardButton("🔙 رجوع للمادة", callback_data=f"sem_{spec_code}_{sem_code}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode="Markdown")

    elif data == "main_menu":
        context.user_data["uploading"] = False
        await start(update, context)

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # التأكد أن المستخدم دخل قسماً معيناً ويريد رفع ملف
    if not context.user_data.get("uploading"):
        await update.message.reply_text("يرجى اختيار التخصص والسمستر والمادة والقسْم أولاً قبل إرسال الملف.")
        return

    spec_code = context.user_data.get("current_spec")
    sem_code = context.user_data.get("current_sem")
    subj_name = context.user_data.get("current_subj")
    sec_code = context.user_data.get("current_sec")

    document = update.message.document or update.message.video or update.message.photo[-1] if update.message.photo else None
    
    if not document:
        await update.message.reply_text("لم يتم التعرف على الملف، حاول إرساله كملف (Document).")
        return

    if update.message.document:
        file_id = update.message.document.file_id
        file_name = update.message.document.file_name or "ملف بدون اسم"
    elif update.message.video:
        file_id = update.message.video.file_id
        file_name = "فيديو محاضرة"
    else:
        file_id = update.message.photo[0].file_id
        file_name = "صورة توضيحية"

    # حفظ الملف في قاعدة البيانات
    conn = sqlite3.connect("uofk_bot.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO files (specialty, semester, subject, section, file_id, file_name) VALUES (?, ?, ?, ?, ?, ?)",
        (spec_code, sem_code, subj_name, sec_code, file_id, file_name)
    )
    conn.commit()
    conn.close()

    await update.message.reply_text(f"✅ تم رفع وحفظ الملف ({file_name}) بنجاح في المادة: {subj_name}!")

def main():
    TOKEN = "8768205999:AAE-q0vESQ6paNNd7CKWYA7TkkwzCRy3bng"

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.Document.ALL | filters.VIDEO | filters.PHOTO, handle_document))

    print("البوت يعمل الآن بنجاح...")
    application.run_polling()

if __name__ == "__main__":
    main()
