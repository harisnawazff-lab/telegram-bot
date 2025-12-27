from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import sqlite3

TOKEN = 8410563728:AAE2twiF5nyeRPuHEAT9-YhsVw2t6LJ8Hv8
ADMIN_ID = 6952043184

conn = sqlite3.connect("data.db", check_same_thread=False)
c = conn.cursor()

c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, balance INTEGER)")
c.execute("CREATE TABLE IF NOT EXISTS keys (id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT, price INTEGER)")
conn.commit()

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome!\nSend: username,password")

def login(update: Update, context: CallbackContext):
    if "," not in update.message.text:
        return
    username, password = update.message.text.split(",")
    uid = update.message.from_user.id

    c.execute("SELECT * FROM users WHERE id=?", (uid,))
    user = c.fetchone()

    if not user:
        c.execute("INSERT INTO users VALUES (?,?,?,?)", (uid, username, password, 0))
        conn.commit()
        update.message.reply_text("Account created. Balance: 0")
    elif user[2] == password:
        update.message.reply_text(f"Login success. Balance: {user[3]}")
    else:
        update.message.reply_text("Wrong password")

def addbalance(update: Update, context: CallbackContext):
    if update.message.from_user.id != ADMIN_ID:
        return
    uid = int(context.args[0])
    amt = int(context.args[1])
    c.execute("UPDATE users SET balance = balance + ? WHERE id=?", (amt, uid))
    conn.commit()
    update.message.reply_text("Balance added")

def addkey(update: Update, context: CallbackContext):
    if update.message.from_user.id != ADMIN_ID:
        return
    price = int(context.args[0])
    key = " ".join(context.args[1:])
    c.execute("INSERT INTO keys (key, price) VALUES (?,?)", (key, price))
    conn.commit()
    update.message.reply_text("Key added")

def buy(update: Update, context: CallbackContext):
    uid = update.message.from_user.id
    c.execute("SELECT id, key, price FROM keys LIMIT 1")
    k = c.fetchone()
    if not k:
        update.message.reply_text("No keys available")
        return

    c.execute("SELECT balance FROM users WHERE id=?", (uid,))
    bal = c.fetchone()[0]

    if bal < k[2]:
        update.message.reply_text("Not enough balance")
        return

    c.execute("DELETE FROM keys WHERE id=?", (k[0],))
    c.execute("UPDATE users SET balance = balance - ? WHERE id=?", (k[2], uid))
    conn.commit()
    update.message.reply_text(f"Your key:\n{k[1]}")

updater = Updater(TOKEN)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("addbalance", addbalance))
dp.add_handler(CommandHandler("addkey", addkey))
dp.add_handler(CommandHandler("buy", buy))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, login))

updater.start_polling()
updater.idle()
