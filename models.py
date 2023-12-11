# Import the necessary components from the SQLAlchemy library, which is a toolkit for SQL database interaction.

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import Table, Column, Integer, ForeignKey
from dbextension import db
import datetime

# Create an instance of the SQLAlchemy class.
# This object will be used to interact with the database.


# Define an association table for a many-to-many relationship between Words and Tags.
# This is needed because a word can have many tags and a tag can be associated with many words.
word_tags = Table('word_tags', db.Model.metadata,
    Column('word_id', Integer, ForeignKey('word.id'), primary_key=True),  # Link to the Word table.
    Column('tag_id', Integer, ForeignKey('tag.id'), primary_key=True)    # Link to the Tag table.
)
# Model for logging changes to the database
class ChangeLog(db.Model):
    # Unique identifier for each log entry
    id = db.Column(db.Integer, primary_key=True)
    # Name of the table where the change occurred
    table_name = db.Column(db.String(128), nullable=False)
    # ID of the record that was changed
    record_id = db.Column(db.Integer, nullable=False)
    # Type of action performed ('insert', 'update', 'delete')
    action = db.Column(db.String(128), nullable=False)
    # Timestamp of when the change was made
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    # Optional details about the change
    details = db.Column(db.String(1024))
    
# Define a User model, which will be used to create a table in the database.
# Models in Flask-SQLAlchemy are used to represent database tables.
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # A unique identifier for each user.
    username = db.Column(db.String(50), unique=True, nullable=False)  # User's username, must be unique and present.
    email = db.Column(db.String(50), unique=True, nullable=False)  # User's email, must be unique and present.
    # Add more fields as needed for additional user information, like passwords, etc.

# Define a Quiz model for database table creation.
# Each quiz will have a unique ID and a title.
class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # A unique identifier for each quiz.
    title = db.Column(db.String(100))  # The title of the quiz.
    # You can add more quiz attributes like description, difficulty, etc.

# Define a UserProgress model to track the progress of a user.
class UserProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # A unique identifier for each progress record.
    user_id = db.Column(db.Integer, ForeignKey('user.id'))  # The ID of the user, linked to the User model.
    word_id = db.Column(db.Integer, ForeignKey('word.id'))  # The ID of the word, linked to the Word model.
    progress = db.Column(db.String(50))  # Progress status, like 'learning', 'mastered', etc.
    user = relationship("User", backref="progresses")  # Sets up a relationship to the User model.
    word = relationship("Word", backref="progresses")  # Sets up a relationship to the Word model.

# Define a UserSettings model to store user settings.
class UserSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # A unique identifier for each setting.
    user_id = db.Column(db.Integer, ForeignKey('user.id'))  # The ID of the user, linked to the User model.
    setting = db.Column(db.String(100))  # The name of the setting.
    value = db.Column(db.String(100))    # The value of the setting.
    user = relationship("User", backref="settings")  # Sets up a relationship to the User model.

# Define a Session model to store user session data.
class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # A unique identifier for each session.
    user_id = db.Column(db.Integer, ForeignKey('user.id'))  # The ID of the user, linked to the User model.
    session_data = db.Column(db.String(500))  # A field to store any data related to the user session.
    user = relationship("User", backref="sessions")  # Sets up a relationship to the User model.

# Define a Word model to store words in the database.
class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # A unique identifier for each word.
    japanese = db.Column(db.String(100), nullable=False)  # The word in Japanese, must be present.
    english = db.Column(db.String(100))  # The word in English.
    tags = relationship('Tag', secondary=word_tags, backref='words')  # Sets up the many-to-many relationship to the Tag model.

# Define a Tag model to store tags in the database.
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # A unique identifier for each tag.
    name = db.Column(db.String(50), unique=True, nullable=False)  # The name of the tag, must be unique and present.

# Define a Report model to store Reports in the database.
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    content = db.Column(db.Text, nullable=False)

