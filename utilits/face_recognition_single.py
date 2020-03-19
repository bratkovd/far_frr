import face_recognition

def recognition(photo_1, photo_2):
    person_1 = face_recognition.load_image_file(photo_1)
    person_2 = face_recognition.load_image_file(photo_2)

    person_1_encoding = face_recognition.face_encodings(person_1)[0]
    person_2_encoding = face_recognition.face_encodings(person_2)[0]

    percent = None

    percent = face_recognition.face_distance([person_1_encoding], person_2_encoding)[0]

    return percent

if __name__ == '__main__':
    photo_1 = 'E:\\lfw_mvd\\match\\1000009_РИЗВАН_ИБАДУЛЛАЕВИЧ_ИБРАГИМГАДЖИЕВ\\РИЗВАН_ИБАДУЛЛАЕВИЧ_ИБРАГИМГАДЖИЕВ_1147823.PNG'
    photo_2= 'E:\\lfw_mvd\\match\\1000009_РИЗВАН_ИБАДУЛЛАЕВИЧ_ИБРАГИМГАДЖИЕВ\\РИЗВАН_ИБАДУЛЛАЕВИЧ_ИБРАГИМГАДЖИЕВ_1147824.PNG'

    print(recognition(photo_1, photo_2))