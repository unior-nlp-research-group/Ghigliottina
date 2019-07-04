
def test_pymongo():
    from pymongo import MongoClient
    from bson.objectid import ObjectId

    # http://api.mongodb.com/python/current/tutorial.html

    # for mongo engine (more class oriented) see
    # http://docs.mongoengine.org/tutorial.html

    # connect to MongoDB
    client = MongoClient('localhost', 27017)

    # create database
    db = client['test-database']

    # create collection
    collection = db['test-collection']

    # create document
    test_doc = {
        "_id": "new",
        "hello": "world"
    }

    # insert test document
    post_id = collection.insert_one(test_doc).inserted_id
    print(post_id)

    # list all collections in db (excluding the system ones)
    db.list_collection_names()

    my_doc = collection.find_one(post_id)
    collection.find_one({"_id": post_id})
    collection.find_one({"_id": ObjectId('5cbdee4b79ba41599a853b81')})
    # my_doc = test_coll.find_one('_id': post_id)

def test_mongoengine():
    from mongoengine import connect, Document, StringField, DictField
    connect('Lexicon')

    class Word(Document):
        name = StringField(primary_key=True)
        patterns = DictField()

    # w = Word(name='parola', patterns = {'a': 'b'})
    w = Word.objects.get(name='parola')    
    # new_pattern = {'patterns': {'a': {'e': 'e'}}}
    new_key_values = {"key1": "value1", "key2": "value2"}
    set_new_key_values = dict((("set__patterns__{}".format(k), v) for k,v in new_key_values.items()))
    Word.objects.get(pk='parola').update(**set_new_key_values)
    Word.objects.get(pk='parola').update(inc__counter)
    

    # for w in Word.objects:
    #     print(w.name)

    # w = Word.objects.get(name='parola')    
    # print(w.name)
    # .get()
    # print(w.name)

    # w = Word(name = 'parola', patterns = {})
    # w.save()
    # print(w.pk)



if __name__ == "__main__":
    # test_pymongo()
    test_mongoengine()