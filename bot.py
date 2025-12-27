from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import sqlite3

TOKEN = "8410563728:AAE2twiF5nyeRPuHEAT9-YhsVw2t6LJ8Hv8"
ADMIN_ID = 6952043184  # apni admin id yahin rehne do

conn = sqlite3.connect("data.db", check_same_thread=False)
c = conn.cursor()

c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, balance INTEGER)")
c.execute("CREATE TABLE IF NOT EXISTS keys (id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT, price INTEGER)")
conn.commit()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome!\nSend username,password")


async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "," not in update.message.text:
        return

    username, password = update.message.text.split(",")
    uid = update.message.from_user.id

    c.execute("SELECT * FROM users WHERE id=?", (uid,))
    user = c.fetchone()

    if not user:
        c.execute("INSERT INTO users VALUES (?,?,?,?)", (uid, username, password, 0))
        conn.commit()
        await update.message.reply_text("Account created. Balance: 0")
    elif user[2] == password:
        await update.message.reply_text(f"Login success. Balance: {user[3]}")
    else:
        await update.message.reply_text("Wrong password")


async def addbalance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return
    uid = int(context.args[0])
    amt = int(context.args[1])
    c.execute("UPDATE users SET balance = balance + ? WHERE id=?", (amt, uid))
    conn.commit()
    await update.message.reply_text("Balance added")


async def addkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return
    price = int(context.args[0])
    key = " ".join(context.args[1:])
    c.execute("INSERT INTO keys (key, price) VALUES (?,?)", (key, price))
    conn.commit()
    await update.message.reply_text("Key added")


async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    c.execute("SELECT id, key, price FROM keys LIMIT 1")
    k = c.fetchone()

    if not k:
        await update.message.reply_text("No keys available")
        return

    c.execute("SELECT balance FROM users WHERE id=?", (uid,))
    bal = c.fetchone()[0]

    if bal < k[2]:
        await update.message.reply_text("Not enough balance")
        return

    c.execute("DELETE FROM keys WHERE id=?", (k[0],))
    c.execute("UPDATE users SET balance = balance - ? WHERE id=?", (k[2], uid))
    conn.commit()
    await update.message.reply_text(f"Your key:\n{k[1]}")


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("addbalance", addbalance))
app.add_handler(CommandHandler("addkey", addkey))
app.add_handler(CommandHandler("buy", buy))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, login))

app.run_polling()