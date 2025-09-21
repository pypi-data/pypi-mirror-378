Full-Stack Django + React + TailwindCSS ⚡

A one-command starter for a full-stack app with Django (backend) and React + TailwindCSS + Vite (frontend) — all in a single repo. Auto-configures for development and production.

## Windows:
- py -m pip install django-react-cli
- py -m django-react-cli

## Linux
python3 -m pip install django-react-cli
python3 -m django-react-cli


## 📦 Features

### Frontend

- ⚡ **Vite + React + TailwindCSS**
- 🛠️ Auto-generated `vite.config.js` and `index.css`
- 🌐 Env-based settings via `config.json`
- 🎨 Preconfigured fonts and theme

### Backend

- 🐍 **Django + Django REST Framework**
- 🔐 Token-based authentication
- 🌍 CORS support via `django-cors-headers`
- 📦 Whitenoise for static file handling
- 🗄️ SQLite (development) / PostgreSQL (production)
- 🌐 Env-based settings via `config.json`

### Extras

- 📁 Unified directory structure for frontend and backend
- ⚙️ Auto-generated `config.json` for easy environment switching
- 🚀 Django templates serve Vite dev server in development and built static files in production

---

## 🛠 Requirements

- **Python 3.8+**  
- **Node.js 18+ & npm**  
- **pip** (comes with Python)  
- **PostgreSQL** (only needed in production)

---

## Project Structure

```bash

your-project/
│── account/          # Django app
│── core/             # Django project
│── src/              # React source
│── static/           # Collected static files
│── dist/             # React build (prod)
│── env/              # Python virtualenv
│── media/            # Uploaded files
│── template/         # Django templates
│── config.json
│── requirements.txt
│── vite.config.js
│── manage.py
│── package.json
│── index.css

```

##  License
 django-react-cli is licensed under the MIT License.

## Contacto

[LinkedIn](https://www.linkedin.com/in/hugo345?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=android_app) hugo aragon