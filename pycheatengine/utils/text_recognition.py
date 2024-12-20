import pytesseract
from pytesseract import Output

pytesseract.pytesseract.tesseract_cmd = r'D:\Tesseract\tesseract.exe'

def detect_text_in_scene(scene):
    """
    Detects all text on the screen and retrieves their coordinates.
    Returns:
        list of dict: A list of dictionaries containing text and bounding box coordinates.
    """
    # Perform OCR on the screenshot
    ocr_data = pytesseract.image_to_data(scene, output_type=Output.DICT, config='--oem 1 --psm 1')

    detected_text = []
    for i in range(len(ocr_data['text'])):
        text = ocr_data['text'][i].strip()
        if text:  # Ignore empty strings
            x, y, w, h = (ocr_data['left'][i], ocr_data['top'][i],
                          ocr_data['width'][i], ocr_data['height'][i])
            detected_text.append({
                'text': text,
                'x_min': x,
                'y_min': y,
                'x_max': x + w,
                'y_max': y + h
            })

    return detected_text