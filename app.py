from flask import Flask
from routes.logger import logger 
from routes.recommender import recommender
from routes.projector import projector

app = Flask(__name__)

# Register the recommender blueprint
app.register_blueprint(logger, url_prefix="/logger")
app.register_blueprint(recommender, url_prefix="/recommender")
app.register_blueprint(projector, url_prefix="/projector")

if __name__ == '__main__':
    app.run(debug=True)