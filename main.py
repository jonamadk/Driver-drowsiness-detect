from flask import Flask, Response , request 

from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow



app = Flask(__name__)
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
db= SQLAlchemy(app)
ma = Marshmallow(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    set_alarm = db.Column(db.Boolean, unique = False, default = True)
    
class PostSchema(ma.Schema):
    class Meta:
        fields = ('id','set_alarm')
        
post_schema = PostSchema()
posts_schema = PostSchema(many=True)


class PostsResource(Resource):
    def get(self):
        return posts_schema.dump(Post.query.all())
    
    
    def post(self):
        
        data = request.json
        post = Post(set_alarm = data['set_alarm'])
        db.session.add(post)
        db.session.commit()
        return post_schema.dump(post)
    
    
    
class PostResource(Resource):
    def get(self,pk):
        return post_schema.dump(Post.query.get_or_404(pk))
    
    

    def patch(self,pk):
        data = request.json 
        post = Post.query.get_or_404(pk)
        
        if 'set_alarm' in data:
            post.set_alarm = data['set_alarm']
        
        db.session.commit()
        return post_schema.dump(post)
    
#     def delete(self,pk):
#         post = Post.query.get_or_404(pk)
#         db.session.delete(post)
#         db.session.commit()
#         return '',204
    
    
api.add_resource(PostResource,'/post/<int:pk>')
    
api.add_resource(PostsResource,'/posts')


    
if __name__ =='__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)
    
    
    
