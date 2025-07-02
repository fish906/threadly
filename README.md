# Threadly

**Threadly** is a lightweight, secure, and extensible topic-based webhook message service built with **Flask** and **MariaDB**. Use it to receive, store, and manage messages from various sources via simple webhooks, organized by topics.



## 🚀 Features

- **Topic-based architecture** — Group messages by named topics for easy organization.
- **Secure publishing** — Authenticate incoming webhooks with hashed publisher keys.
- **Retention policies** — Automatically clean up old messages per topic.
- **Command-line tools** — Manage topics, view and delete messages easily with the built-in CLI.
- **Simple and extensible** — Minimal dependencies, easy to adapt to your needs.



## 📌 Use Cases

- Centralized webhook receiver for IoT, microservices, or third-party apps.
- Store and inspect incoming notifications.
- Build custom integrations that need a simple message bus.
- Queue lightweight messages for later processing.



## ⚙️ Tech Stack

- **Backend:** Python, Flask
- **Database:** MariaDB
- **CLI:** Typer for easy command-line management

## 🚦 Roadmap
- Message forwarding: Fan-out to other webhooks and/or email
- Retention rules per topic: Current default is 90 days
- Rate Limiting
- Edit topics and keys: Allowing rotating keys
- Enabling attachments: User may upload files or include links
- Scheduled messages: Allow scheduling messages to be sent later automatically.
- Dockerization



## 📖 Getting Started
**tbd**

## 🛡️ License
MIT — feel free to use and adapt!

## 🙌 Contributing
Pull requests are welcome! If you have ideas for new features or improvements, please open an issue!