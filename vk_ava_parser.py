import vk_api
import psycopg2
import logging
import face_interactor

# Setup VK API
vk_session = vk_api.VkApi('user', 'password')
vk_session.auth()
vk = vk_session.get_api()

# Initiate local values
logging.basicConfig(filename="ava.log", level=logging.INFO)

offset = 0
connection_db = psycopg2.connect("user='' password='' host='' dbname=''")
db = connection_db.cursor()

def log(string):
    print(string)
    logging.info(string)

def registerOffset(value):
    log("register offset {}".format(value))
    query = "INSERT INTO parser({}, {}) VALUES({}, {});".format('userid', 'source', value, 2)
    db.execute(query)
    connection_db.commit()

def lastOffset():
    queryUserId = "SELECT userid FROM parser WHERE source = 2 ORDER BY userid DESC LIMIT 1 "
    db.execute(queryUserId)
    result = db.fetchone()
    if result == None:
        result = 1
    else:
        result = result[0]
    return result

def getCountPeoples():
    queryUserId = "SELECT COUNT(*) FROM (SELECT DISTINCT file FROM vectors) AS temp;"
    db.execute(queryUserId)
    result = db.fetchone()
    return result[0]

def getCountImages():
    queryUserId = "SELECT COUNT(*) FROM (SELECT file FROM vectors) AS temp;"
    db.execute(queryUserId)
    result = db.fetchone()
    return result[0]
log("wet")
offset = lastOffset()
log("last offset: {}".format(offset))

try:
    offset_at_start = offset
    session_faces = 0
    while True:
        log("------------------")
        log("total added peoples: {}".format(getCountPeoples()))
        log("session processed peoples: {}".format(offset - offset_at_start))
        log("session added faces: {}".format(session_faces))
        log("total processed images: {}".format(getCountImages()))
        log("------------------")
        # searchResult = vk.users.search(fields='screen_name', has_photo='1', offset='{}'.format(offset))

        # create list of usersId

        user_ids_int_array = list(range(offset, offset + 10))
        param_user_ids = ', '.join(str(x) for x in user_ids_int_array)
        print('generated list id for request: {}'.format(param_user_ids))

        searchResult = vk.users.get(user_ids=param_user_ids, fields='photo_200, verified')
        for item in searchResult:
            userName = item['first_name'] + ' ' + item['last_name']
            userName = userName.replace('\'', '')
            link = item['id']
            log("----------------")
            log("fetched user: {}".format(userName))

            if 'deactivated' in item:
                log('deactivated')
                offset = offset + 1
                registerOffset(offset)
                continue

            if item['can_access_closed'] == False:
                offset = offset + 1
                registerOffset(offset)
                log('closed profile')
                continue

            found_faces = 0

            if 'photo_200' in item:
                # working with images
                photo = item['photo_200']
                registeredFaces = face_interactor.process_picture_url(link, photo, userName, 2, db, connection_db)
                if registeredFaces > 0:
                    log("+")
                    found_faces = found_faces + registeredFaces
                    connection_db.commit()
                else:
                    log("-")
                log("found {} faces".format(found_faces))
            else:
                log("without photo")

            offset = offset + 1
            registerOffset(offset)
            session_faces = session_faces + found_faces

except Exception as e:
    print('crash {}'.format(str(e)))
    if connection_db is not None:
        connection_db.close()


if connection_db is not None:
    connection_db.close()






#session = vk.Session(access_token='3d9c64b579cb4d22a1aa066635a6a9331eae919725e33aff659e5306473f627a9f3f310f0c868cec37655')
