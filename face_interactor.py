import dlib
import face_recognition
from skimage import io
import logging

def process_picture_url(link, imagePath, userName, serviceId, db, connection_db):
    try:
        face_detector = dlib.get_frontal_face_detector()
        image = io.imread(imagePath)

        # logging.info("processing image: {}".format(imagePath))

        # Run the HOG face detector on the image data
        detected_faces = face_detector(image, 1)
        if len(detected_faces) == 0:
            # logging.info("ignore image, face not found")
            return 0

        add_face_counter = 0
            # Loop through each face we found in the image
        for i, face_rect in enumerate(detected_faces):
            # Detected faces are returned as an object with the coordinates
            # of the top, left, right and bottom edges
            crop = image[face_rect.top():face_rect.bottom(), face_rect.left():face_rect.right()]
            encodings = face_recognition.face_encodings(crop)

            if len(encodings) > 0:
                query = "INSERT INTO vectors (file, vec_low, vec_high, imagepath, sourceid, username, link) VALUES ('{}', CUBE(array[{}]), CUBE(array[{}]), '{}', '{}', '{}', '{}');".format(
                    '',
                    ','.join(str(s) for s in encodings[0][0:63]),
                    ','.join(str(s) for s in encodings[0][64:127]),
                    imagePath,
                    serviceId,
                    userName,
                    link)
                db.execute(query)
                connection_db.commit()
                # logging.info('success')
                add_face_counter = add_face_counter + 1
            else:
                logging.info('error encoding [{}]'.format(imagePath))
        return add_face_counter
    except Exception as e:
        logging.info("Exception: {}".format(str(e)))
        return 0

