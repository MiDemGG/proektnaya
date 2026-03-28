import os
import fitz  # PyMuPDF
from google import genai
from google.genai import types

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("❌ Ошибка: Не задан GEMINI_API_KEY!")
    exit(1)

# Инициализируем клиента
client = genai.Client(api_key=API_KEY)

def process_document(file_path):
    """Извлекает изображение из файла и подготавливает его для Gemini"""
    if file_path.lower().endswith('.pdf'):
        print(f"📄 Извлекаю страницу из PDF...")
        doc = fitz.open(file_path)
        page = doc[0]
        pix = page.get_pixmap(dpi=150) 
        img_data = pix.tobytes("jpeg")
        doc.close()
        return types.Part.from_bytes(data=img_data, mime_type="image/jpeg")
    else:
        print(f"🖼️ Подготавливаю изображение...")
        with open(file_path, "rb") as f:
            img_data = f.read()
        mime_type = "image/png" if file_path.lower().endswith('.png') else "image/jpeg"
        return types.Part.from_bytes(data=img_data, mime_type=mime_type)

def extract_xml_from_image(image_part):
    """Отправляет картинку в Gemini и просит полный XML всего документа"""
    print("🧠 Gemini анализирует текст... (подождите)")
    
    prompt = """
    Ты - эксперт по оцифровке документов. Перед тобой скан университетского заявления (содержит как печатный, так и рукописный текст).
    Твоя задача: перенести ВЕСЬ текст с изображения в структурированный XML-формат. Ничего не пропускай.
    
    Сгруппируй распознанный текст по логическим блокам. Используй примерно такую структуру тегов (можешь добавлять свои, если текст не влезает в эти):
    <Document>
      <Header>
        </Header>
      <ApplicantInfo>
        </ApplicantInfo>
      <Title>ЗАЯВЛЕНИЕ</Title>
      <Body>
        </Body>
      <Signatures>
        </Signatures>
      <Approvals>
        </Approvals>
    </Document>
    
    Важные правила:
    1. Распознавай и печатный, и рукописный текст. Объединяй их так, чтобы предложения имели смысл (вставляй рукописные слова на место пропусков в печатном тексте).
    2. Если какое-то поле на бланке не заполнено рукой студента, не выдумывай текст, оставь тег пустым или напиши "не заполнено".
    3. Верни ТОЛЬКО чистый XML-код. Без markdown-разметки (```xml), без комментариев и лишнего текста в начале или конце.
    """

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[prompt, image_part],
        config=types.GenerateContentConfig(
            temperature=0.0,
        )
    )
    
    return response.text.strip()

if __name__ == '__main__':
    # Настройки папок
    INPUT_DIR = "БЛАНК"
    OUTPUT_DIR = "XML"
    
    # Проверяем, существует ли папка с исходниками
    if not os.path.exists(INPUT_DIR):
        print(f"❌ Папка '{INPUT_DIR}' не найдена! Создайте ее рядом со скриптом и положите туда сканы.")
        exit()
        
    # Создаем папку для готовых XML (если ее нет)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Ищем файлы (jpg, png, pdf)
    valid_extensions = ('.jpg', '.jpeg', '.png', '.pdf')
    files_to_process = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(valid_extensions)]
    
    if not files_to_process:
        print(f"⚠️ В папке '{INPUT_DIR}' нет подходящих файлов для обработки.")
        exit()
        
    print(f"📂 Найдено файлов для обработки: {len(files_to_process)}")
    print("="*50)

    # Запускаем цикл по всем найденным файлам
    for filename in files_to_process:
        file_path = os.path.join(INPUT_DIR, filename)
        
        # Получаем имя файла без расширения (например: "акад_page-0001")
        base_name = os.path.splitext(filename)[0]
        output_path = os.path.join(OUTPUT_DIR, f"{base_name}.xml")
        
        print(f"▶️ В работе: {filename}")
        
        try:
            image_part = process_document(file_path)
            xml_result = extract_xml_from_image(image_part)
            
            # Очистка от возможных markdown-тегов (```xml ... ```)
            if xml_result.startswith("```xml"):
                xml_result = xml_result.replace("```xml\n", "", 1).replace("```", "")
            elif xml_result.startswith("```"):
                xml_result = xml_result.replace("```\n", "", 1).replace("```", "")
                
            xml_result = xml_result.strip()
                
            # Сохраняем в папку XML
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(xml_result)
                
            print(f"✅ Сохранено: {output_path}")
            print("-" * 50)

        except Exception as e:
            print(f"❌ Ошибка при обработке {filename}: {e}")
            print("-" * 50)
            
    print("🎉 Обработка всех бланков завершена!")
