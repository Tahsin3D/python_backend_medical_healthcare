import easyocr
import numpy as np
import time

start_time = time.time()

reader = easyocr.Reader(['en'])
result = reader.readtext('tt.jpeg')

end_time = time.time()

elapsed_ms = (end_time - start_time) * 1000

CONFIDENCE_THRESHOLD = 0.5
LINE_Y_THRESHOLD = 20  # pixels tolerance to consider text on the same line

# Extract useful data
words = []
for box, text, conf in result:
    if conf >= CONFIDENCE_THRESHOLD and text.strip():
        top_left_y = box[0][1]
        center_y = (box[0][1] + box[2][1]) // 2
        x = box[0][0]
        words.append({'text': text.strip(), 'x': x, 'y': center_y})

# Group words by lines using y-coordinate proximity
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

# Sort words in each line left-to-right and join them
final_lines = []
for line in lines:
    sorted_line = sorted(line, key=lambda w: w['x'])
    line_text = ' '.join(w['text'] for w in sorted_line)
    final_lines.append(line_text)

# Combine all lines
final_output = '\n'.join(final_lines)

# Print the result
print("Extracted Text (Grouped Horizontally by Lines):\n")
print(final_output)

print(f"OCR completed in {elapsed_ms:.2f} ms")