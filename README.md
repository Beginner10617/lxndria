# Lxndria.com
Lxndria is an open-source web platform inspired by the discontinued [*The Brilliant Community*](https://brilliant.org/community-faq/). It focuses on problem-solving and discussions rather than course-based learning. The goal is to create an interactive and engaging space for knowledge-sharing, logical problem-solving, and collaborative discussions.

## 🚀 Features  

- 🧠 **Problem-Solving Discussions** – Users can engage in deep discussions on problem statements.  
- 📚 **Open Learning Platform** – Encourages learning through active participation rather than structured courses.  
- 🌐 **Web-Based Interface** – Accessible through any modern web browser.    
- ⚡ **Flask-Based Backend** – The backend is built using Python's Flask framework.  
- 🔄 **Open Source** – Contributions are welcome to expand the platform's functionality.  

---

## 🏗️ Tech Stack  

- **Backend:** Flask (Python)  
- **Frontend:** HTML, CSS, JavaScript  
- **Database:** PostgreSQL  
- **Hosting:** Google Cloud
- **Version Control:** Git & GitHub  

---

## 📦 Installation & Setup  

### Prerequisites  

Ensure you have the following installed:  

- Python 3.x  
- Flask  
- Git  

### Steps to Run Locally  

1. **Clone the repository:**  
   ```bash
   git clone https://github.com/Beginner10617/lxndria
   cd lxndria
   ```
2. **Create a virtual environment (optional but recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate   # On Windows use: venv\Scripts\activate
    ```
3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Set Up Environment Variables:**

    Create a .env file in the root directory and add required variables:
    ```bash
    SECRET_KEY=your-secret-key
    FERNET_KEY=your-fernet-key
    EMAIL_ID=your-email-id
    EMAIL_PASSWORD=app-password
    UPLOAD_FOLDER=profile-pic-upload
    EMAIL_SERVER=smtp.gmail.com # Change if using any other server
    DATABASE_URI=sqlite:///db.sqlite3  # Change if using PostgreSQL/MySQL
    ```
5. **Apply Database Migrations:**
    ```bash
    flask db upgrade  # If using Flask-Migrate
    ```
    OR if manually setting up a database:
    ```bash
    flask db init
    flask db migrate -m "Initial migration"
    flask db upgrade
    ```
6. **Run the Development server:**
    ```bash
    flask run
    ```
7. **Access the app at:**
    ```
    http://127.0.0.1:5000
    ```

---

## 🚀 Deployment
Lxndria is intended for production deployment. Consider:

- Setting up a secure Flask server (e.g., using gunicorn)
- Using Nginx or Apache for - reverse proxy
- Deploying on cloud platforms (e.g., DigitalOcean, AWS, Google Cloud)
- Implementing SSL/TLS for security

---

## 🛠️ Contributing

We welcome contributions! If you'd like to contribute:

1. Fork the repository
2. Create a new branch
3. Make your changes and commit
4. Open a pull request

---

## 📜 License  

Lxndria.com is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.  

See the full license details in the [`LICENSE`](https://github.com/Beginner10617/lxndria/blob/main/LICENSE) file.  

---

## 📬 Contact

- **Website:** [lxndria.com](https://lxndria.com) (Currently not hosting)
- **GitHub Issues:** Report Issues [Here](https://github.com/Beginner10617/lxndria/issues)
- **Email:** wasihusain23@iitk.ac.in

---

## 🌟 Support the Project
If you find this project valuable, consider giving a ⭐ on GitHub!
