import os
import xml.etree.ElementTree as ET
from flask import Flask, request, jsonify
import cv2 
import easyocr
import fitz  

app = Flask(__name__)

print("Загружаю нейросеть EasyOCR. Пожалуйста, подожди...")
# Возвращаем EasyOCR для русского и английского
reader = easyocr.Reader(['ru', 'en'])
print("Нейросеть успешно загружена и готова к работе!")

def preprocess_image(input_path, output_path):
    """Улучшаем картинку перед распознаванием"""
    print("OpenCV: Начинаю улучшение качества картинки...")
    img = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
    img_blur = cv2.medianBlur(img, 3)
    thresh = cv2.adaptiveThreshold(
        img_blur, 255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    cv2.imwrite(output_path, thresh)
    print("OpenCV: Картинка успешно улучшена!")

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'Нет файла в запросе'}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'Файл не выбран'}), 400

    try:
        filename = file.filename.lower()
        extracted_text = "" 

        # --- ВЕТВКА 1: Работа с PDF ---
        if filename.endswith('.pdf'):
            print("Получен PDF документ...")
            temp_pdf_path = "temp_document.pdf"
            file.save(temp_pdf_path)

            doc = fitz.open(temp_pdf_path)
            
            for page_num, page in enumerate(doc):
                print(f"Обрабатываю страницу {page_num + 1}...")
                pix = page.get_pixmap()
                
                temp_page_path = f"temp_page_{page_num}.jpg"
                enhanced_page_path = f"enhanced_page_{page_num}.jpg"
                
                pix.save(temp_page_path)
                
                # 1. Сначала улучшаем
                preprocess_image(temp_page_path, enhanced_page_path)

                # 2. Затем читаем с помощью EasyOCR (передаем улучшенную картинку)
                result = reader.readtext(enhanced_page_path, detail=0)
                extracted_text += " ".join(result) + "\n"

                for p in [temp_page_path, enhanced_page_path]:
                    if os.path.exists(p): os.remove(p)
            
            doc.close()
            if os.path.exists(temp_pdf_path): os.remove(temp_pdf_path)

        # --- ВЕТВКА 2: Работа с Картинкой ---
        else:
            print("Получена фотография...")
            temp_path = "temp_image.jpg"
            enhanced_path = "enhanced_image.jpg"
            file.save(temp_path)

            # 1. Сначала улучшаем
            preprocess_image(temp_path, enhanced_path)

            # 2. Читаем с помощью EasyOCR
            result = reader.readtext(enhanced_path, detail=0)
            extracted_text = " ".join(result)

            for p in [temp_path, enhanced_path]:
                if os.path.exists(p): os.remove(p)

        print("Распознанный текст:\n", extracted_text)

        root = ET.Element("Document")
        text_element = ET.SubElement(root, "ExtractedText")
        text_element.text = extracted_text if extracted_text.strip() else "Текст не распознан"

        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ", level=0) 
        tree.write("output.xml", encoding="utf-8", xml_declaration=True)

        return jsonify({'message': 'Файл успешно обработан OpenCV + EasyOCR!', 'text_length': len(extracted_text)}), 200

    except Exception as e:
        return jsonify({'error': f'Произошла ошибка: {str(e)}'}), 500

if __name__ == '__main__':
    print("Сервер запущен! Жду фото/PDF на порту 7777...")
    app.run(host='0.0.0.0', port=7777)
