import random
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

TOKEN = "PASTE_YOUR_BOT_TOKEN_HERE"

# ---------------- CHATBOT LINES ----------------
SAVAGE_LINES = [
    "😈 Galat move tha bhai",
    "💀 Screenshot le, yaad rahega",
    "😏 Dimag off mode detected",
    "🔥 Risk lena mehnga pad gaya"
]

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("❌⭕ XO Kill", callback_data="xo")],
        [InlineKeyboardButton("🔫 Roulette", callback_data="roulette")],
        [InlineKeyboardButton("💣 Bomb Pass", callback_data="bomb")],
        [InlineKeyboardButton("⚡ Fast Tap", callback_data="fasttap")],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ]
    await update.message.reply_text(
        "💀 **KILL GAME ARENA**\nChoose your death 😈",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# ---------------- HELP ----------------
async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🎮 **HELP**\n\n"
        "❌⭕ XO = 3 in row = KILL\n"
        "🔫 Roulette = 1 bullet\n"
        "💣 Bomb = random blast\n"
        "⚡ Fast Tap = slow = dead\n\n"
        "No typing. Only tap 😈",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("⬅ Back", callback_data="back")]]
        )
    )

# ---------------- XO GAME ----------------
def new_board():
    return ["⬜"] * 9

def board_markup(board):
    buttons = []
    for i in range(0, 9, 3):
        row = [
            InlineKeyboardButton(board[i], callback_data=f"xo_{i}"),
            InlineKeyboardButton(board[i+1], callback_data=f"xo_{i+1}"),
            InlineKeyboardButton(board[i+2], callback_data=f"xo_{i+2}")
        ]
        buttons.append(row)
    buttons.append([InlineKeyboardButton("🏳 Surrender", callback_data="back")])
    return InlineKeyboardMarkup(buttons)

def check_win(b):
    wins = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    for a,b1,c in wins:
        if b[a] != "⬜" and b[a] == b[b1] == b[c]:
            return True
    return False

async def xo_start(update, context):
    query = update.callback_query
    await query.answer()
    board = new_board()
    context.user_data["board"] = board
    await query.edit_message_text(
        "❌⭕ **XO KILL GAME**\nYour turn ❌\n\n" + random.choice(SAVAGE_LINES),
        parse_mode="Markdown",
        reply_markup=board_markup(board)
    )

async def xo_move(update, context):
    query = update.callback_query
    await query.answer()
    board = context.user_data.get("board")
    idx = int(query.data.split("_")[1])

    if board[idx] != "⬜":
        return

    board[idx] = "❌"
    if check_win(board):
        await query.edit_message_text("☠️ **YOU KILLED THE BOT** 😈", parse_mode="Markdown")
        return

    empty = [i for i,v in enumerate(board) if v=="⬜"]
    if not empty:
        await query.edit_message_text("💣 DRAW! Sudden death avoided")
        return

    board[random.choice(empty)] = "⭕"
    if check_win(board):
        await query.edit_message_text("💀 **BOT EXECUTED YOU**\n" + random.choice(SAVAGE_LINES), parse_mode="Markdown")
        return

    await query.edit_message_text(
        "❌⭕ XO KILL\nYour turn 😏",
        reply_markup=board_markup(board)
    )

# ---------------- ROULETTE ----------------
async def roulette(update, context):
    query = update.callback_query
    await query.answer()
    if random.randint(1,6) == 1:
        text = "💀 **BANG! You are dead**"
    else:
        text = "😎 Click survived. Lucky!"
    await query.edit_message_text(text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Back", callback_data="back")]])
    )

# ---------------- BOMB ----------------
async def bomb(update, context):
    query = update.callback_query
    await query.answer()
    result = random.choice(["💣 BOOM! Dead", "😅 Passed safely"])
    await query.edit_message_text(
        result,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Back", callback_data="back")]])
    )

# ---------------- FAST TAP ----------------
async def fasttap(update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "⚡ **FAST TAP!**\nClick NOW!",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔥 TAP", callback_data="tap_result")]])
    )

async def tap_result(update, context):
    query = update.callback_query
    await query.answer()
    if random.choice([True, False]):
        msg = "🔥 FAST! You survived"
    else:
        msg = "💀 TOO SLOW! Dead"
    await query.edit_message_text(
        msg,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅ Back", callback_data="back")]])
    )

# ---------------- CALLBACK ROUTER ----------------
async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.callback_query.data

    if data == "xo":
        await xo_start(update, context)
    elif data.startswith("xo_"):
        await xo_move(update, context)
    elif data == "roulette":
        await roulette(update, context)
    elif data == "bomb":
        await bomb(update, context)
    elif data == "fasttap":
        await fasttap(update, context)
    elif data == "tap_result":
        await tap_result(update, context)
    elif data == "help":
        await help_menu(update, context)
    elif data == "back":
        await start(update.callback_query, context)

# ---------------- MAIN ----------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_router))
    print("🔥 Kill Game Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()