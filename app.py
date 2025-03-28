from flask import Flask, render_template, request, send_file
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image
from reportlab.lib.colors import HexColor
import qrcode
import os
from datetime import datetime
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

app = Flask(__name__)

# Настройка валюты
CURRENCY = "KZT"
CUSTOM_PAGE_SIZE = (600, 320)  # Формат 16:9 (ширина x высота)

# Регистрация шрифта Arial для поддержки кириллицы
pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))

# Расположение элементов
TEXT_X_1 = 470  # Горизонтальное положение текста
TEXT_Y_1 = 130  # Вертикальное положение текста
TEXT_X_2 = 307  # Горизонтальное положение текста
TEXT_Y_2 = 88.5  # Вертикальное положение текста
TEXT_X_3 = 410
TEXT_Y_3 = 10
QR_X = 525      # Горизонтальное положение QR-кода
QR_Y = 0    # Вертикальное положение QR-кода

ToTime = datetime.today()
time = f"Выдан: {ToTime.day}.{ToTime.strftime('%m')}.{ToTime.year}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_certificate():
    certificate_number = request.form['certificate_number']
    amount = request.form['amount']

    # Генерация QR-кода
    qr = qrcode.make(f"Номер сертификата: {certificate_number}, Сумма: {amount} {CURRENCY}")
    qr_filename = f"temp_qr_{certificate_number}.png"
    qr.save(qr_filename)

    # Генерация PDF
    output_filename = f"Сертификат_{certificate_number}.pdf"
    pdf = canvas.Canvas(output_filename, pagesize=CUSTOM_PAGE_SIZE)

    # Добавляем переднюю сторону сертификата
    front_image = "certificate_front_x3.png"  # Передняя сторона
    if os.path.exists(front_image):
        pdf.drawInlineImage(front_image, 0, 0, width=612, height=313)

    # Устанавливаем шрифт Arial
    pdf.setFont("Arial", 27)
    pdf.setFillColor(HexColor("#5d5d5d"))
    pdf.drawString(TEXT_X_1, TEXT_Y_1, f"{certificate_number}")  # номер
    pdf.setFont("Arial", 17)
    pdf.drawString(TEXT_X_2, TEXT_Y_2, f"{amount} KZT")  # сумма

    # Добавляем заднюю сторону сертификата
    pdf.showPage()  # Переход на новую страницу
    back_image = "certificate_back.png"  # Задняя сторона
    if os.path.exists(back_image):
        pdf.drawInlineImage(back_image, 0, 0, width=612, height=313)

    pdf.setFont("Arial", 12)
    pdf.drawString(TEXT_X_3, TEXT_Y_3, time)  # Дата
    pdf.drawInlineImage(qr_filename, QR_X, QR_Y, width=75, height=75)

    # Сохраняем PDF
    pdf.save()

    # Удаляем временный QR-код
    os.remove(qr_filename)

    # Возвращаем PDF для скачивания
    return send_file(output_filename, as_attachment=True, download_name=f"Сертификат_{certificate_number}.pdf")

if __name__ == '__main__':
    app.run(debug=True)
