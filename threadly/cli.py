# cli.py

import typer
import uvicorn
from . import server
from threadly.db import SessionLocal, Base, engine
from threadly import crud, utils, models
from threadly import logger

app = typer.Typer(help="Manage your webhook server & messages")

topic_app = typer.Typer(help="Manage topics")
message_app = typer.Typer(help="Manage messages")

app.add_typer(topic_app, name="topic")
app.add_typer(message_app, name="message")

# -----------------------------
# INIT DB
# -----------------------------
Base.metadata.create_all(bind=engine)

# -----------------------------
# SERVE COMMAND
# -----------------------------
@app.command()
def serve(host: str = "0.0.0.0", port: int = 5000):
    """
    Start the Flask webhook server.
    """
    from . import server  # ensure server.py runs with Flask's app
    server.app.run(host=host, port=port)

# -----------------------------
# TOPIC COMMANDS
# -----------------------------
@topic_app.command("add")
def add_topic():
    """
    Add a new topic.
    """
    db = SessionLocal()
    try:
        name = typer.prompt("Enter topic name").strip()
        # Check if topic exists
        exists = crud.get_topic_by_name(db, name)
        if exists:
            typer.echo(f"❌ Topic '{name}' already exists. Pick a different name.")
            raise typer.Exit()

        key = typer.prompt("Enter secure key", hide_input=True, confirmation_prompt=True)

        crud.create_topic(db, name, key)
        typer.echo(f"✅ Topic '{name}' created.")

    finally:
        db.close()

@topic_app.command("list")
def list_topics():
    """
    List all topics.
    """
    db = SessionLocal()
    try:
        topics = db.query(models.Topic).all()
        if not topics:
            typer.echo("No topics found.")
            return
        for t in topics:
            typer.echo(f"- {t.id}: {t.name} (created at {t.created_at})")
    finally:
        db.close()

@topic_app.command("edit")
def edit_topic(
    topic: str = typer.Option(..., help="Current topic name"),
    new_name: str = typer.Option(None, help="New topic name"),
    new_publisher_key: str = typer.Option(None, help="New publisher key"),
):
    """
    Edit an existing topic's name and/or publisher key.
    """
    db = SessionLocal()
    try:
        topic_obj = crud.get_topic_by_name(db, topic)
        if not topic_obj:
            typer.echo(f"❌ Topic '{topic}' does not exist.")
            raise typer.Exit()

        updated = crud.update_topic(db, topic_obj.id, new_name=new_name, new_publisher_key=new_publisher_key)
        if updated:
            typer.echo(f"✅ Topic updated successfully.")
            if new_name:
                typer.echo(f"- New name: {updated.name}")
            if new_publisher_key:
                typer.echo("- Publisher key updated.")
        else:
            typer.echo("❌ Failed to update topic.")
    finally:
        db.close()

# -----------------------------
# MESSAGE COMMANDS
# -----------------------------
@message_app.command("list")
def list_messages(
    topic: str = typer.Option(..., help="Name of the topic to list messages from"),
    limit: int = typer.Option(10, help="Number of messages to show"),
):
    """
    List messages for a topic.
    """
    db = SessionLocal()
    try:
        topic_obj = crud.get_topic_by_name(db, topic)
        if not topic_obj:
            typer.echo(f"❌ Topic '{topic}' does not exist.")
            raise typer.Exit()

        messages = crud.get_messages_for_topic(db, topic_obj.id, limit)
        if not messages:
            typer.echo("No messages found.")
            return

        for m in messages:
            typer.echo(f"[{m.id}] {m.created_at} | {m.title} | {m.body}")

    finally:
        db.close()

@message_app.command("delete")
def delete_message(
    message_id: int = typer.Option(..., help="Input message id!")
):
    """
    Delete a message by its ID.
    """
    db = SessionLocal()
    try:
        message = crud.get_message_by_id(db, message_id)
        if not message:
            typer.echo(f"❌ Message {message_id} not found.")
            raise typer.Exit()
        
        # Access related data while session is open
        topic_name = message.topic.name
        
        crud.delete_message_by_id(db, message_id)
        typer.echo(f"✅ Message {message_id} deleted.")
        
        logger.logger.info(f"Message deleted via CLI: ID={message_id}, Topic={topic_name}, Title={message.title}")

    finally:
        db.close()

# -----------------------------
# CLEANUP COMMAND
# -----------------------------
@app.command("cleanup")
def cleanup(days: int = 90):
    """
    Delete messages older than the retention period.
    """
    db = SessionLocal()
    try:
        deleted = crud.cleanup_old_messages(db, days)
        typer.echo(f"✅ Deleted {deleted} old messages (>{days} days).")
    finally:
        db.close()

if __name__ == "__main__":
    app()
