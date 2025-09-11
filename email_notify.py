import smtplib
from email.mime.text import MIMEText

EMAIL_SENDER = "fileuseingbyds@gmail.com"
EMAIL_PASSWORD = "rdrd tmef lqxq ookk"
EMAIL_RECEIVER = "fileuseingbyds@gmail.com"

def send_email(subject, message):
    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print("❌ 傳送失敗：", e)

# --- 測試區塊 ---
if __name__ == "__main__":
    test_subject = "測試郵件"
    test_message = "這是一封測試用的郵件，來自 Raspberry Pi 或 Python 程式。"
    send_email(test_subject, test_message)
