import requests
import logging


class DTOPeople:
    def __init__(self, json):
        self.id = json['id']
        self.name = json['name'].replace('\'', '')
        self.imdb_id = json['imdb_id']


class DTOFullPeople:
    def __init__(self, info, images):
        self.info = info
        self.images = images


api_key = ""
api_url = "http://api.themoviedb.org/3"
logging.basicConfig(filename="app.log", level=logging.INFO)


def getPeopleDetails(id):
    url = "{}/person/{}?api_key={}&language=en-US".format(api_url, id, api_key)
    logging.info('Fetch people data for id: {}'.format(id))
    print('Fetch people data for id: {}'.format(id))
    try:
        request = requests.get(url)
        json = request.json()
        if request.status_code == 200:
            people = DTOPeople(json)
            logging.info('name: {}'.format(people.name))
            print('name: {}'.format(people.name))
            return people
        elif request.status_code == 422:
            logging.info('id is not valid integer')
            print('id is not valid integer')
            return None
        else:
            error_message = json['status_message']
            logging.info(error_message)
            print(error_message)
            return None
    except Exception:
        logging.info('bad json: {}'.format(json))
        print('bad json: {}'.format(json))
        return None


def getImagesForPeople(id):
    url = "{}/person/{}/images?api_key={}&language=en-US".format(api_url, id, api_key)
    request = requests.get(url)
    json = request.json()
    images = list()
    if request.status_code == 200:
        for image in json['profiles']:
            imageUrl = 'https://image.tmdb.org/t/p/w200/{}'.format(image['file_path'])
            images.append(imageUrl)
        logging.info("found {} images".format(len(images)))
        print("found {} images".format(len(images)))
        return images
    elif request.status_code == 422:
        logging.info('id is not valid integer')
        print('id is not valid integer')
        return None
    else:
        error_message = json['status_message']
        logging.info(error_message)
        print(error_message)
        return None


def getFullPeople(id):
    try:
        info = getPeopleDetails(id)
        if info is None:
            return None
        images = getImagesForPeople(id)
        if info is None or images is None or len(images) is 0:
            return None
        else:
            return DTOFullPeople(info, images)
    except Exception:
        return None
