# HealthVision (Pharmapulse)

A multilingual Flask web app that recommends over-the-counter drugs based on user-described symptoms, powered by a MySQL backend and a BERTweet sentiment model for feedback analysis.

## Overview

HealthVision (branded in the UI as "Pharmapulse") helps everyday users get quick, general guidance on which over-the-counter drugs are commonly used for a health condition or symptom, and look up dosage/side-effect information for a specific drug — in English or Hindi. It is **not** a diagnostic tool and always tells users to consult a doctor.

**Who it's for:** people who want a fast, conversational first pass at "what do people usually take for X" before seeing a healthcare professional.

**Key features:**
- Conversational chatbot UI for describing symptoms and getting drug suggestions
- Drug information lookup (description, dosage, side effects) for known drugs
- English and Hindi input/output, with automatic language detection and translation
- User accounts with a health survey (existing conditions/medications) used to personalize suggestions
- Guest mode (no account required) for quick, anonymous use
- Email-based OTP for registration and password reset
- User feedback on suggested drugs, scored with sentiment analysis and fed back into future rankings
- Account management (update phone number / password)

## Tech Stack

**Backend**
- Python 3.12, Flask 3
- MySQL (via `mysql-connector-python`) — tables for accounts, surveys, drugs, and feedback
- `smtplib` for OTP emails over Gmail SMTP

**ML / NLP**
- `transformers` + `torch` — BERTweet-based sentiment analysis of user feedback (`finiteautomata/bertweet-base-sentiment-analysis`)
- `langid` — language detection
- `deep-translator` (Google Translate backend) — English ⇄ Hindi translation
- `jellyfish` — text similarity for matching user phrasing

**Frontend**
- Server-rendered Jinja2 templates (HTML/CSS/vanilla JS)
- Bootstrap 5, Boxicons for styling/icons

## Project Structure

```
HealthVision/
├── README.md
├── .gitignore
├── ad2.py                  # Flask app entry point (routes, business logic)
├── dbconn.py                # MySQL connection helper
├── Sentiment.py             # BERTweet sentiment analysis wrapper
├── find_nearest.py          # phrase-similarity helper (Levenshtein distance)
├── common_drugs.dat         # pickled: known BP/heart/diabetes medication sets
├── drug_details2.nsk        # pickled: per-drug description/dosage/side-effects
├── requirements.txt
├── .env.example             # template for required environment variables
├── .env                     # your local secrets (not committed)
├── static/
│   ├── chatbot.css
│   ├── liq.css
│   ├── logo2.png
│   ├── favicon.png
│   └── doctor-animate.gif
└── templates/
    ├── login.html
    ├── index.html            # registration
    ├── forget_password.html
    ├── otpSend.html
    ├── reset_password.html
    ├── questions.html        # medical survey
    ├── chatbot.html          # main chat UI
    └── result.html
```

## Prerequisites

- Python 3.10+ (developed/tested on 3.12)
- `pip` for installing dependencies
- Access to a MySQL database (the project was built against a remote MySQL instance; any MySQL 5.7+/8+ server works) with the following tables and stored procedures already created: `LOGIN_DETAILS`, `USER_DETAILS`, `SURVEY_REPORT`, `LOGIN_COUNT`, `DRUG3`, and stored procedures `ADD_USER`, `ADD_SURVEY`, `UPDATE_PASSWORD`, `DELETE_USER`, `INSERT_DRUGS`
- A Gmail account with an [App Password](https://myaccount.google.com/apppasswords) (used to send OTP emails) — regular Gmail passwords will not work with SMTP
- Internet access (the translation feature calls Google Translate, and the sentiment model is downloaded from Hugging Face on first run)

## Getting Started — How to Run Locally

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd HealthVision
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and fill in your real values:
   ```
   EMAIL_ADDRESS=your-email@gmail.com
   EMAIL_APP_PASSWORD=your-gmail-app-password
   DB_HOST=your-mysql-host
   DB_USER=your-mysql-username
   DB_PASSWORD=your-mysql-password
   DB_NAME=your-mysql-database-name
   PORT=5000
   ```

5. **Start the app**
   ```bash
   python ad2.py
   ```
   The first run will download the BERTweet sentiment model from Hugging Face, which can take a few minutes.

6. **Open it in your browser**
   ```
   http://127.0.0.1:5000
   ```
   (or whatever port you set in `PORT`)

## Features

- **Login / Registration** — Email + password accounts, with OTP email verification at signup and for password resets.
- **Guest Mode** — Skip account creation and go straight to the chatbot with a "Guest Mode" link on the login page.
- **Health Survey** — New users are asked about existing conditions (BP, heart disease, diabetes) and current medications, used to flag when a suggested drug might interact with what they're already taking.
- **Symptom Chatbot** — Type (or speak, via the browser's speech recognition) a symptom or condition (e.g. "I have rheumatoid arthritis") and get back a ranked list of commonly used, positively-reviewed drugs for that condition.
- **Drug Info Lookup** — Ask about a specific drug (e.g. "what is paracetamol") to get its description, dosage, and side effects.
- **Multilingual Support** — Select English or Hindi from the chat UI; symptoms and responses are automatically translated.
- **Feedback Loop** — After trying a suggested drug, users can rate it; the free-text feedback is scored with a sentiment model and used to adjust future rankings for that drug.
- **Account Management** — Update phone number and/or password from the account popup in the chatbot view.

[Screenshot placeholder — add image of the login page here]
[Screenshot placeholder — add image of the chatbot conversation here]
[Screenshot placeholder — add image of the drug info response here]

## API Endpoints

| Method | Route | Description |
|---|---|---|
| GET | `/` | Login page |
| POST | `/index` | Authenticate login credentials |
| GET | `/loginOpen` | Render login page |
| POST | `/register` | Create a new user account |
| GET | `/renderIndexPage` | Render registration page |
| GET | `/questionsOpen` | Render the health survey page |
| POST | `/questions` | Submit health survey answers |
| GET | `/guest` | Enter guest mode chatbot |
| POST | `/med` | Confirm/update existing medications after login |
| POST | `/predict` | Submit a symptom/question, get a drug suggestion or drug info |
| POST | `/go_to_chatbot` | Submit feedback/rating for a suggested drug |
| POST | `/update` | Update account phone number / password |
| GET | `/forgot_password` | Render forgot-password page |
| POST | `/gop` | Request an OTP for password reset |
| POST | `/v_otp` | Verify a password-reset OTP |
| POST | `/otpAuthentication` | Send a registration OTP email |
| POST | `/reset_password` | Set a new password |
| POST | `/doesExist` | Check whether an email is already registered |
| GET | `/logout` | Log out and return to login page |

## Future Improvements

- Implement the `/predict_image` endpoint referenced by the frontend (image-based symptom/prescription upload is not yet wired up on the backend)
- Move stored-procedure-based database access to parameterized queries / an ORM to reduce SQL injection risk
- Add server-side OTP verification before account creation (currently enforced only in the browser)

## License

MIT License

Copyright (c) 2026 HealthVision

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
