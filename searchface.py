
import dlib
import face_recognition
import os
import psycopg2
from skimage import io
import json
from psycopg2.extras import RealDictCursor
import logging

logging.basicConfig(filename="searcher.log", level=logging.INFO)

def search_by_image(image):
    try:
        # Create a HOG face detector using the built-in dlib class
        face_detector = dlib.get_frontal_face_detector()
        jsonResult = '{}'
        # Load the image
        image = image

        # Run the HOG face detector on the image data
        detected_faces = face_detector(image, 1)
        if (len(detected_faces) == 0):
            return "{\"errorCode\": 1 }"

        if (len(detected_faces) > 1):
            return "{\"errorCode\": 2 }"

        if not os.path.exists("./.faces"):
            os.mkdir("./.faces")

        connection_db = psycopg2.connect("user='' password='' host='' dbname=''")
        db = connection_db.cursor(cursor_factory=RealDictCursor)

        # Loop through each face we found in the image
        for i, face_rect in enumerate(detected_faces):
            # Detected faces are returned as an object with the coordinates
            # of the top, left, right and bottom edges

            crop = image[face_rect.top():face_rect.bottom(), face_rect.left():face_rect.right()]
            encodings = face_recognition.face_encodings(crop)

            print(encodings)
            threshold = 0.68
            if len(encodings) > 0:
                query2 = "SELECT sqrt(power(CUBE(array[{}]) <-> vec_low, 2) + power(CUBE(array[{}]) <-> vec_high, 2)) as euclid, file, imagepath FROM vectors ORDER BY euclid ASC LIMIT 10".format(
                    ','.join(str(s) for s in encodings[0][0:63]),
                    ','.join(str(s) for s in encodings[0][64:127]),
                    threshold
                )
                print(query2)
                db.execute(query2)
                jsonResult = json.dumps(db.fetchall(), indent=2)
            else:
                print("No encodings")

        if connection_db is not None:
            connection_db.close()

        return jsonResult
    except Exception as e:
        logging.info('exception: {}'.format(e))
        return "{\"errorCode\": 3}" #, \"exception\": {}}".format(str(e))

def search_by_file_name(file_name):
    image = io.imread(file_name)
    return search_by_image(image)

