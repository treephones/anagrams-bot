from screenshot import Screenshot
from itertools import permutations
from time import sleep
import cv2
import pytesseract
import json
import serial

def threshold(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

def get_all_words(string):
    words = {
        6: [],
        5: [],
        4: [],
        3: []
    }

    def get_threes(string): #works because string is never larger than 6
        ret = []
        for i in range(len(string)):
            for j in range(len(string)):
                for k in range(len(string)):
                    comb = string[i] + string[j] + string[k]
                    if comb not in ret:
                        ret.append(comb)
        return ret

#remove repeating letters from get_fours and get_threes
    def get_fours(string):
        ret = []
        for i in range(len(string)):
            for j in range(len(string)):
                for k in range(len(string)):
                    for g in range(len(string)):
                        comb = string[i] + string[j] + string[k] + string[g]
                        if comb not in ret:
                            ret.append(comb)
        return ret

    def get_fives(string):
        ret, d = [], []
        for l in list(string):
            if l not in d:
                on = string.replace(l, "")
                d.append(l)
            ret += list(map(''.join, permutations(on)))
        return ret

    with open("engl_dict.json") as file:
        dict = json.load(file)

    possibs = list(map(''.join, permutations(string))) #largest
    possibs += get_fives(string)
    possibs += get_fours(string)
    possibs += get_threes(string)

    for p in possibs:
        try:
            if dict[p] == 1:
                dict[p] = 2  # already used
                words[len(p)].append(p)
        except KeyError:
            # not a word
            continue
    return words

capture = Screenshot("LonelyScreen AirPlay Receiver")
print("Press 's' when you are on the screen with the letters visible:")

while True:
    frame = capture.get_frame()
    cv2.imshow("Screen", frame)

    if cv2.waitKey(1) == ord('s'):
        cv2.destroyAllWindows()
        break

frame = cv2.cvtColor(capture.crop(frame), cv2.COLOR_BGR2GRAY)
frame = threshold(frame)
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Moez\AppData\Local\Tesseract-OCR\tesseract.exe'

config = r'--oem 3 --psm 6'
letters = "".join(list(pytesseract.image_to_string(frame, config=config))[:-2]).lower()
all_words = get_all_words(letters)
coords = {
    letters[0]: (1,1),
    letters[1]: (1,1),
    letters[2]: (1,1),
    letters[3]: (1,1),
    letters[4]: (1,1),
    letters[5]: (1,1)
}
s = serial.Serial(
    port="",
    baudrate=38400
)

for word in all_words:
    for letter in word:
        s.write([coords[letter][i] for i in range(2)])
        sleep(0.2)

#show image after done
while True:
    cv2.imshow("Processed", frame)
    if cv2.waitKey(1) == ord('s'):
        cv2.destroyAllWindows()
        break