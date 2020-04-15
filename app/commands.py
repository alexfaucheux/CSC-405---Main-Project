import click
from flask.cli import with_appcontext
from flask import url_for
from app.extensions import db



@click.command(name='create_tables')
@with_appcontext
def create_tables():
    db.create_all()


@click.command(name='fill_image_table')
@with_appcontext
def fill_image_table():
    from app.models import Image
    images = ["images/img-1.jpg", "images/img-2.jpg", "images/img-3.jpg", "images/img-4.jpg",
              "images/img-5.jpg", "images/meteor.jpg", "images/moon.jpg", "images/stars.jpg"]

    for i in range(len(images)):
        img_obj = Image(image_name="Image {}".format(i), image_url=url_for('static', filename=images[i]))
        db.session.add(img_obj)

    db.session.commit()
