# db_operations.py
from dbextension import db
from models import  User, Word
#Tag, ChangeLog, Report
from sqlalchemy.exc import SQLAlchemyError

# User CRUD Operations
def add_user(username, email):
    try:
        new_user = User(username=username, email=email)
        db.session.add(new_user)
        db.session.commit()
        add_change_log('User', new_user.id, 'insert', f'Added user {username}')
        return "User added successfully"
    except SQLAlchemyError as e:
        return f"Error adding user: {e}"
def get_users():
    try:
        return User.query.all()
    except SQLAlchemyError as e:
        return f"Error fetching users: {e}"


def get_users():
    try:
        return User.query.all()
    except SQLAlchemyError as e:
        return f"Error fetching users: {e}"

def update_user(user_id, new_username, new_email):
    try:
        user = User.query.get(user_id)
        if user:
            user.username = new_username
            user.email = new_email
            db.session.commit()
            add_change_log('User', user.id, 'update', f'Updated user {new_username}')
            return True
        return False
    except SQLAlchemyError as e:
        return f"Error updating user: {e}"

def delete_user(user_id):
    try:
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            add_change_log('User', user.id, 'delete', f'Deleted user')
            return True
        return False
    except SQLAlchemyError as e:
        return f"Error deleting user: {e}"



# Tag CRUD Operations
# Implement similar functions for add_tag, get_tags, update_tag, delete_tag
def add_word(japanese, english):
    try:
        # Check if the word already exists in the database
        existing_word = Word.query.filter_by(japanese=japanese).first()
        if existing_word:
            return "Word already exists"

        # If the word doesn't exist, add it to the database
        new_word = Word(japanese=japanese, english=english)
        db.session.add(new_word)
        db.session.commit()
        return "Word added successfully"
    except SQLAlchemyError as e:
        # Properly aligned 'except' block
        return f"Error adding word: {e}"


def get_words():
    try:
        return Word.query.all()
    except SQLAlchemyError as e:
        return f"Error fetching words: {e}"

def update_word(word_id, new_japanese, new_english):
    try:
        word = Word.query.get(word_id)
        if word:
            word.japanese = new_japanese
            word.english = new_english
            db.session.commit()
            add_change_log('Word', word.id, 'update', f'Updated word {new_japanese}')
            return True
        return False
    except SQLAlchemyError as e:
        return f"Error updating word: {e}" 
    
def delete_word(word_id):
    word = Word.query.get(word_id)
    if word:
        db.session.delete(word)
        db.session.commit()
        return True
    else:
        return False

def add_tag(name):
    tag = Tag(name=name)
    db.session.add(tag)
    db.session.commit()
    return "Tag added successfully"

def get_tags():
    return Tag.query.all()

def update_tag(tag_id, new_name):
    tag = Tag.query.get(tag_id)
    if tag:
        tag.name = new_name
        db.session.commit()
        return "Tag updated successfully"
    else:
        return "Tag not found"

def delete_tag(tag_id):
    tag = Tag.query.get(tag_id)
    if tag:
        db.session.delete(tag)
        db.session.commit()
        return "Tag deleted successfully"
    else:
        return "Tag not found"   

def add_change_log(table_name, record_id, action, details=None):
    try:
        new_log = ChangeLog(table_name=table_name, record_id=record_id, action=action, details=details)
        db.session.add(new_log)
        db.session.commit()
    except SQLAlchemyError as e:
        return f"Error adding change log: {e}"

def generate_report():
    try:
        logs = ChangeLog.query.order_by(ChangeLog.timestamp.desc()).all()
        report_content = "\n".join([f"{log.timestamp}: {log.action} on {log.table_name} (ID: {log.record_id}) - {log.details}" for log in logs])
        new_report = Report(content=report_content)
        db.session.add(new_report)
        db.session.commit()
        return new_report.id
    except SQLAlchemyError as e:
        return f"Error generating report: {e}"
    
    #Difficult words functionality \
    


# Continue to define other necessary functions (like reset_database_data)
