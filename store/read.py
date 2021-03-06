'''
DB Read Service
---------------
'''
import logging
from bson.objectid import ObjectId
from util import debug
from . import mongo

log = logging.getLogger(__name__)

def get_movies():
    db = mongo.get_db()
    movies = list(db.movies.find())
    if movies:
        for i, item in enumerate(movies):
            movies[i] = item['title']
    return movies

def get_reviews(movie_title):
    db = mongo.get_db()
    reviews = list(db.reviews.find({"itemReviewed.name": movie_title}))
    if not reviews:
        log.info("No reviews found for " + str(movie_title))
    return reviews

def get_movie_info(movie_title):
    db = mongo.get_db()
    movie_info = db.movies.find_one({"title": movie_title})
    if not movie_info or not movie_info['info']:
        log.info("No moview info found for " + str(movie_title))
        return None
    movie_info['info']['key'] = movie_title
    return movie_info['info']

def read_by_id(collection, object_id):
    if not isinstance(object_id, ObjectId):
        object_id = ObjectId(object_id)
    db = mongo.get_db()
    cursor = db[collection].find({'_id': object_id})
    for document in cursor:
        return document
    log.info('No data found for id ' + str(object_id))
    return None

def find(collection, condition, col=None):
    db = mongo.get_db()
    cursor = db[collection].find(condition, col)
    return cursor

def query(collection, condition, col=None):
    cursor = find(collection, condition, col)
    return [item for item in cursor]

def smart_query(collection, condition):
    """
    Smart query is smart because it provide both
    """
    smart_condition = list()
    for condition_key, condition_value in condition.iteritems():
        if isinstance(condition_value, dict):
            # We do not optimize complicate conditions.
            smart_condition.append({condition_key: condition_value})
        else:
            smart_condition.append({"$or": [
                {condition_key: condition_value},
                {condition_key: None},
                {condition_key: {"$exists": False}}
            ]})
    query_condition = {"$and": smart_condition}
    debug.print_as_json(query_condition)
    return query(collection, query_condition)
