import datetime as dt
import hashlib
import os
import re
import secrets
import smtplib
import sqlite3
import time
import json
import base64
from email.message import EmailMessage
from functools import wraps
from urllib.parse import parse_qs, urlencode
from urllib.request import Request, urlopen

from flask import Flask, flash, g, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "portal.db")
SECRET_PATH = os.path.join(BASE_DIR, ".secret_key")

ADMIN_SEED_USERS = [
    ("bgoodwill", "WTF!over2001"),
    ("bkettle", "WTF!over2001"),
]
PAYPAL_URL = "https://paypal.me/blakegoodwill"
PAYPAL_BUSINESS = os.environ.get("PAYPAL_BUSINESS", "blakeg716@hotmail.com")
PAYPAL_CURRENCY = os.environ.get("PAYPAL_CURRENCY", "USD")
PAYPAL_CHECKOUT_BASE = os.environ.get("PAYPAL_CHECKOUT_BASE", "https://www.paypal.com/cgi-bin/webscr")
PAYPAL_IPN_VERIFY_URL = os.environ.get("PAYPAL_IPN_VERIFY_URL", "https://ipnpb.paypal.com/cgi-bin/webscr")
# PayPal Commerce Platform (for expanded checkout methods: PayPal, Venmo, Pay Later, Cards)
PAYPAL_CLIENT_ID = os.environ.get("PAYPAL_CLIENT_ID", "")
PAYPAL_CLIENT_SECRET = os.environ.get("PAYPAL_CLIENT_SECRET", "")
PAYPAL_API_SANDBOX = os.environ.get("PAYPAL_API_SANDBOX", "1") == "1"
PAYPAL_API_BASE = "https://api-m.sandbox.paypal.com" if PAYPAL_API_SANDBOX else "https://api-m.paypal.com"
PORTAL_PUBLIC_BASE_URL = os.environ.get("PORTAL_PUBLIC_BASE_URL", "").strip().rstrip("/")
AUTO_APPROVE_PAID_WITH_PAYMENT_REF = True
try:
    _AUTO_REJECT_PENDING_MINUTES_RAW = int(os.environ.get("AUTO_REJECT_PENDING_MINUTES", "30"))
except ValueError:
    _AUTO_REJECT_PENDING_MINUTES_RAW = 30
AUTO_REJECT_PENDING_MINUTES = max(10, min(_AUTO_REJECT_PENDING_MINUTES_RAW, 30))
FREE_RENEW_COOLDOWN_MINUTES = 5
SUPPORT_EMAIL = "blakeg716@hotmail.com"
APP_NAME = "TheBlakes Portal"

SMTP_HOST = os.environ.get("PORTAL_SMTP_HOST", "")
try:
    SMTP_PORT = int(os.environ.get("PORTAL_SMTP_PORT", "587"))
except ValueError:
    SMTP_PORT = 587
SMTP_USER = os.environ.get("PORTAL_SMTP_USER", "")
SMTP_PASS = os.environ.get("PORTAL_SMTP_PASS", "")
SMTP_FROM = os.environ.get("PORTAL_SMTP_FROM", SMTP_USER)
SMTP_USE_TLS = os.environ.get("PORTAL_SMTP_USE_TLS", "1") == "1"

PLAN_CONFIG = {
    "FREE": {
        "label": "Free",
        "price": 0,
        "minutes": 35,
        "days": None,
        "features": {
            "allow_both": False,
            "allow_burst": False,
            "limited": True,
            "allow_themes": False,
            "allow_profiles": False,
            "allow_packs": False,
            "allow_loadouts": False,
            "allow_secondary_keyboard": False,
            "min_speed_ms": 50,
            "max_speed_ms": 10000,
            "max_games": 2,
        },
    },
    "DAY1": {"label": "4 Days", "price": 4, "days": 4, "features": {"allow_both": True, "allow_burst": True, "limited": False, "allow_secondary_keyboard": True, "min_speed_ms": 10, "max_speed_ms": 1000}},
    "DAY7": {"label": "8 Days", "price": 15, "days": 8, "features": {"allow_both": True, "allow_burst": True, "limited": False, "allow_secondary_keyboard": True, "min_speed_ms": 10, "max_speed_ms": 1000}},
    "DAY60": {"label": "60 Days", "price": 30, "days": 60, "features": {"allow_both": True, "allow_burst": True, "limited": False, "allow_secondary_keyboard": False, "min_speed_ms": 10, "max_speed_ms": 1000}},
    "LIFE": {"label": "Unlimited", "price": 100, "days": 54750, "features": {"allow_both": True, "allow_burst": True, "limited": False, "allow_secondary_keyboard": True, "min_speed_ms": 1, "max_speed_ms": 1000}},
}

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$ ")
USERNAME_RE = re.compile(r"^[a-zA-Z0-9_.-]{3,32}$")


def is_valid_email(value):
    return bool(EMAIL_RE.match(value or ""))


def is_valid_username(value):
    return bool(USERNAME_RE.match(value or ""))


def is_strong_password(value):
    if len(value or "") < 7:
        return False
    has_letter = any(ch.isalpha() for ch in value)
    has_digit = any(ch.isdigit() for ch in value)
    has_symbol = any(not ch.isalnum() for ch in value)
    return has_letter and has_digit and has_symbol


def token_hash(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def is_renewable_plan(plan_code):
    conf = PLAN_CONFIG.get(plan_code)
    if not conf:
        return False
    if plan_code == "LIFE":
        return False
    return conf["price"] > 0 and conf["days"] is not None


def compute_expiry_iso(conf):
    minutes = conf.get("minutes")
    if minutes is not None:
        expires = dt.datetime.utcnow() + dt.timedelta(minutes=int(minutes))
        return expires.replace(microsecond=0).isoformat() + "Z"

    days = conf.get("days")
    if days is not None:
        expires = dt.datetime.utcnow() + dt.timedelta(days=days)
        return expires.replace(microsecond=0).isoformat() + "Z"

    return None


def should_defer_expiry_start(plan_code, conf):
    if not conf:
        return False
    if plan_code == "FREE":
        return False
    return float(conf.get("price", 0)) > 0 and (conf.get("minutes") is not None or conf.get("days") is not None)


def read_or_create_secret():
    if os.path.exists(SECRET_PATH):
        with open(SECRET_PATH, "r", encoding="utf-8") as f:
            value = f.read().strip()
            if value:
                return value
    value = secrets.token_hex(24)
    with open(SECRET_PATH, "w", encoding="utf-8") as f:
        f.write(value)
    return value


app = Flask(__name__, static_folder='live_portal/static', template_folder='live_portal/templates')
app.secret_key = read_or_create_secret()
