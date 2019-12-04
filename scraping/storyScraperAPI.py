from flask import Flask, request, jsonify
from flask_restful import reqparse, abort, Api, Resource
from bson.json_util import loads, dumps
from pymongo import MongoClient
from os import environ
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('postId')
parser.add_argument('docId')

def get_db():
    mongo_url = environ['SCRAPING_URL']
    cli = MongoClient(mongo_url)
    db = cli.publicData.stories

    return db
    
class getPostMetadata(Resource):
    def __init__(self, *args, **kwargs):
        self.db = get_db()
        
    def metadata(self, postID, minimal):
        try:
            query = self.db.find({"postID": postID})[0]
            query.pop('_id', None)
        except Exception as e:
            print(f'failed: {e}')
        if minimal == True or minimal == 'True' or minimal == 'true':
            # get content breakdown for one post
            pipeline = [
                {"$match": {"postID": postID}},
                {"$project": {"_id": 0, "docs": "$docs"}},
                {"$unwind": "$docs"},
                {"$group": {"_id": "$docs.mediaType", "count": {"$sum": 1}}},
            ]
            docs_by_type = list(self.db.aggregate(pipeline))
            query['docs'] = docs_by_type
        
        return jsonify(query)
        
    def get(self, minimal=True):
        # parse args
        args = parser.parse_args()
        postID = args['postId']
        if args.get('minimal'):
            minimal = args.get('minimal')
        
        query = self.metadata(postID, minimal)        
        return query

    def post(self, minimal=True):
        # parse args
        args = request.get_json()
        postID = args.get('postId')
        if args.get('minimal'):
            minimal = args.get('minimal')
        
        query = self.metadata(postID, minimal)        
        return query        

class getDocMetadata(Resource):
    def __init__(self, *args, **kwargs):
        self.db = get_db()
        
    def metadata(self, doc_id):
        # find post + doc by doc_id
        try:
            query = self.db.find({'docs': {'$elemMatch': {'doc_id': doc_id}}})
            post = list(query)[0]
            docs = list(filter(lambda x: x['doc_id'] == doc_id, post['docs']))[0]
            docs['content'] = None
            #docs.pop('content', None)
            post['docs'] = docs
            post.pop('_id', None)

            return jsonify(post)
        except Exception as e:
            msg = f'failed: {e}'
            print(msg)
            
            return msg
        
    def get(self):
        # parse args
        args = parser.parse_args()
        doc_id = args['docId']
        
        query = self.metadata(doc_id)        
        return query

    def post(self):
        # parse args
        args = request.get_json()
        doc_id = args.get('docId')
        
        query = self.metadata(doc_id)        
        return query        

api.add_resource(getPostMetadata, '/api/metadataFromPost')
api.add_resource(getDocMetadata, '/api/metadata')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=False)