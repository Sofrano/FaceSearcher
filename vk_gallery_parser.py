import vk_api
import psycopg2
import logging
import face_interactor

# Setup VK API
vk_session = vk_api.VkApi('username', 'password')
vk_session.auth()
vk = vk_session.get_api()

# Initiate local values
logging.basicConfig(filename="vk.log", level=logging.INFO)
offset = 0
connection_db = psycopg2.connect("user='' password='' host='' dbname=''")
db = connection_db.cursor()

def log(string):
    print(string)
    logging.info(string)

def registerOffset(value):
    log("register offset {}".format(value))
    query = "INSERT INTO parser({}, {}) VALUES({}, {});".format('userid', 'source', value, 1)
    db.execute(query)
    connection_db.commit()

def lastOffset():
    queryUserId = "SELECT userid FROM parser WHERE source = 1 ORDER BY userid DESC LIMIT 1 "
    db.execute(queryUserId)
    result = db.fetchone()
    if result == None:
        result = 1
    else:
        result = result[0]
    return result

def getCountPeoples():
    queryUserId = "SELECT COUNT(*) FROM (SELECT DISTINCT link FROM vectors) AS temp;"
    db.execute(queryUserId)
    result = db.fetchone()
    return result[0]

def getCountImages():
    queryUserId = "SELECT COUNT(*) FROM (SELECT link FROM vectors) AS temp;"
    db.execute(queryUserId)
    result = db.fetchone()
    return result[0]

offset = lastOffset()
log("last offset: {}".format(offset))

try:
    offset_at_start = offset
    while True:
        log("------------------")
        log("total processed peoples: {}".format(getCountPeoples()))
        log("session processed peoples: {}".format(offset - offset_at_start))
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
                log('closed profile')
                offset = offset + 1
                registerOffset(offset)
                continue


            # working with images

            is_showed_count_photos = False
            photo_offset = 0
            photo_is_available = True

            found_faces = 0
            added_images = 0
            while photo_is_available:
                # Получаем фотографии
                photos = vk.photos.getAll(owner_id=item['id'], photo_sizes='0', offset='{}'.format(photo_offset))

                # если фотографий больше нет, то берем следущего
                if len(photos['items']) == 0:
                    photo_is_available = False
                    break

                # Если общее кол-во фотографий еще не показывали, то показываем
                if not is_showed_count_photos:
                    max_photos = photos['count']
                    log("count photos: {}".format(max_photos))
                    is_showed_count_photos = True
                    photo_is_available = False # Только первые 20 фотографий юзера разрешаю обработать


                for photo in photos['items']:
                    photoY = list(filter(lambda size: size['type'] == 'x', photo['sizes']))[0]
                    photo_url = photoY['url']
                    registeredFaces = face_interactor.process_picture_url(link, photoY['url'], userName, 1, db, connection_db)
                    if registeredFaces > 0:
                        log("+")
                        added_images = added_images + 1
                        found_faces = found_faces + registeredFaces
                        connection_db.commit()
                    else:
                        log("-")
                photo_offset = photo_offset + len(photos['items'])
                #log("next photos. Offset: {}".format(photo_offset))

            log("{} faces in {} images".format(found_faces, added_images))
            offset = offset + 1
            registerOffset(offset)
except Exception as e:
    print('crash {}'.format(str(e)))
    if connection_db is not None:
        connection_db.close()


if connection_db is not None:
    connection_db.close()






#session = vk.Session(access_token='3d9c64b579cb4d22a1aa066635a6a9331eae919725e33aff659e5306473f627a9f3f310f0c868cec37655')
