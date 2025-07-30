from app import mongo
from bson.objectid import ObjectId
from datetime import datetime, timezone

class Website:
    def __init__(self, title, content, owner_id, business_type=None, industry=None, 
                template_id=None, is_published=False):
        self.title = title
        self.content = content
        self.owner_id = owner_id
        self.business_type = business_type
        self.industry = industry
        self.template_id = template_id
        self.is_published = is_published
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    def save(self):
        website_data = {
            'title': self.title,
            'content': self.content,
            'owner_id': ObjectId(self.owner_id),
            'business_type': self.business_type,
            'industry': self.industry,
            'template_id': self.template_id,
            'is_published': self.is_published,
            'created_at': self.created_at,
            'updated_at': self.updated_at}
        result = mongo.db.websites.insert_one(website_data)
        return str(result.inserted_id)
    
    @staticmethod
    def find_by_id(website_id):
        return mongo.db.websites.find_one({'_id': ObjectId(website_id)})
    
    @staticmethod
    def find_by_owner(owner_id):
        return list(mongo.db.websites.find({'owner_id': ObjectId(owner_id)}))
    
    @staticmethod
    def get_all_websites():
        return list(mongo.db.websites.find({}))
    
    @staticmethod
    def update_website(website_id, data):
        data['updated_at'] = datetime.now(timezone.utc)
        return mongo.db.websites.update_one(
            {'_id': ObjectId(website_id)},
            {'$set': data}
        )
    
    @staticmethod
    def delete_website(website_id):
        return mongo.db.websites.delete_one({'_id': ObjectId(website_id)})
    
    @staticmethod
    def get_published_websites():
        return list(mongo.db.websites.find({'is_published': True}))