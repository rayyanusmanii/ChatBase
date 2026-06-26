# ChatBase

**ChatBase** is a full-stack real-time messaging application built with Flask and Flask-SocketIO. It supports user authentication, group chats, and direct messages, with WebSocket-powered instant delivery and a persistent SQLite database managed through SQLAlchemy ORM.
<img width="1470" height="835" alt="1" src="https://github.com/user-attachments/assets/65c48ae0-351e-42cb-9ff6-cdd3c8b4cd94" /> 
<img width="1470" height="836" alt="2" src="https://github.com/user-attachments/assets/1802819c-21f5-42ad-b3d8-0a405e1be579" />
<img width="1470" height="834" alt="3" src="https://github.com/user-attachments/assets/b2e64ac8-16a7-457a-a2cd-968ba2ef97d8" />

---

## Features

- **User Authentication:** Secure signup and login with Werkzeug password hashing and Flask session management, with a middleware guard protecting all routes.
- **Real-Time Messaging:** WebSocket event handlers enable instant message delivery to all room members without page refreshes.
- **Group Chats:** Users can create named rooms, add members, and chat in a shared space.
- **Direct Messages:** Automatically creates a unique DM room between two users, with deduplication logic to prevent duplicate conversations.
- **Hide Chats:** Users can hide a chat from their sidebar without deleting the shared message history for other members.

---

## Tech Stack
![Python](https://img.shields.io/badge/Python-%233776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-%23000?style=for-the-badge&logo=flask&logoColor=white)
![Flask-SocketIO](https://img.shields.io/badge/Flask--SocketIO-%23010101?style=for-the-badge&logo=socketdotio&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-%23D71F00?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-%23003B57?style=for-the-badge&logo=sqlite&logoColor=white)

---

## Live Demo

[https://web-production-2427a.up.railway.app/](https://web-production-2427a.up.railway.app/)
