from app import create_app, db
from app.models import User, Image, Weather, ObjectOfInterest

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Image': Image, 'Weather': Weather, 'Ob': ObjectOfInterest}
