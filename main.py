from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import easyocr
import numpy as np
import time
from PIL import Image
import io

app = FastAPI()

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
reader = easyocr.Reader(["en"])

@app.post("/ocr")
async def response(file: UploadFile = File(...)):
    image_bytes = await file.read()
    
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image_np = np.array(image)
    
    start_time = time.time()
    result = reader.readtext(image_np)
    end_time = time.time()
    time_taken_by_ocr = round((end_time - start_time),2)
    
    CONFIDENT_THRESHOLD = 0.5
    LINE_Y_THRESHOLD = 20
    
    # Extracting words
    words=[]
    for box, text, conf in result:
        if conf >= CONFIDENT_THRESHOLD and text.strip():
            center_y = (box[0][1] + box[2][1]) // 2
            x = box[0][0]
            words.append({'text': text.strip(), 'x': x, 'y': center_y})
    
    # Grouping words together by line y-coordinate proximity
    lines = []
    for word in sorted(words, key=lambda w: w['y']):
        placed = False
        for line in lines:
            if abs(line[0]['y'] - word['y']) <= LINE_Y_THRESHOLD:
                line.append(word)
                placed = True
                break
        if not placed:
            lines.append([word])

    
    # Sort words in each line left to right and join them
    final_lines = []
    for line in lines:
        sorted_line = sorted(line, key=lambda w: w['x'])
        line_text = ' '.join(w['text'] for w in sorted_line)
        final_lines.append(line_text)
    
    # Combining all lines
    final_output = '\n'.join(final_lines)
    
    print('OCR response generated in: ',time_taken_by_ocr,' seconds.')
    return final_output