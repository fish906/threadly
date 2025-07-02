from sqlalchemy.orm import Session
from . import models, utils

def create_topic(db: Session, name: str, key: str):
    hashed = utils.hash_key(key)
    topic = models.Topic(name=name, key_hash=hashed)
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic

def get_topic_by_name(db: Session, name: str):
    return db.query(models.Topic).filter(models.Topic.name == name).first()

def add_message(db: Session, topic_id: int, title: str, body: str):
    message = models.Message(topic_id=topic_id, title=title, body=body)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

def get_messages_for_topic(db: Session, topic_id: int, limit: int = 10):
    return (
        db.query(models.Message)
        .filter(models.Message.topic_id == topic_id)
        .order_by(models.Message.created_at.desc())
        .limit(limit)
        .all()
    )

def get_message_by_id(db: Session, message_id: int):
    return db.query(models.Message).filter(models.Message.id == message_id).first()

def delete_message_by_id(db: Session, message_id: int):
    message = get_message_by_id(db, message_id)
    if message:
        db.delete(message)
        db.commit()
    return message

def delete_messages_by_topic(db: Session, topic_id: int):
    deleted = db.query(models.Message).filter(models.Message.topic_id == topic_id).delete()
    db.commit()
    return deleted

def cleanup_old_messages(db: Session, days: int = 90):
    from datetime import datetime, timedelta
    cutoff = datetime.utcnow() - timedelta(days=days)
    deleted = db.query(models.Message).filter(models.Message.created_at < cutoff).delete()
    db.commit()
    return deleted

def update_topic(db: Session, topic_id: int, new_name: str = None, new_publisher_key: str = None) -> bool:
    """
    Update topic name and/or publisher key by topic ID.
    Returns True if update succeeded, False otherwise.
    """
    topic = db.query(models.Topic).filter(models.Topic.id == topic_id).first()
    if not topic:
        return False

    if new_name:
        topic.name = new_name
    if new_publisher_key:
        topic.publisher_key = new_publisher_key

    try:
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        # Optionally log the error
        return False

