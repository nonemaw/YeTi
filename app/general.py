
""" this file stores methods for a general access across the application
"""
import bleach
import base64
from Crypto.Cipher import AES
from markdown import markdown
from threading import Thread
from flask import current_app, render_template, request
from flask_mail import Message
from werkzeug.security import check_password_hash
from config import Config

from . import mail
from .db import mongo_connect


def get_company():
    db = mongo_connect('ytml')
    companies = db.Company.find({}).sort([('name', 1)])
    company = []
    for company_dict in companies:
        company.append(company_dict.get('name'))
    return company


def verify_password(password_hash, password):
    return check_password_hash(password_hash, password)


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    """
    using thread to send asyn email in background, non-blocking client
    """
    app = current_app._get_current_object()
    msg = Message(app.config['MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr


def gravatar(avatar_hash, size=100, default='identicon', rating='g'):
    if request.is_secure:
        url = 'https://secure.gravatar.com/avatar'
    else:
        url = 'http://www.gravatar.com/avatar'
    return '{u}/{h}?s={s}&d={d}&r={r}'.format(u=url, h=avatar_hash, s=size,
                                              d=default, r=rating)


def clean_tags(body):
    allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                    'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul', 'h1',
                    'h2', 'h3', 'p']
    return bleach.linkify(bleach.clean(markdown(body, output_format='html'),
                                            tags=allowed_tags, strip=True))


def encrypt(clear_text):
    # a simple password encryption method, better to keep it safe
    enc_secret = AES.new(Config.MASTER_KEY)
    tag_string = (str(clear_text) + (AES.block_size -
                  len(str(clear_text)) % AES.block_size) * "\0")
    cipher_text = base64.b64encode(enc_secret.encrypt(tag_string))
    return cipher_text


def decrypt(cipher_text):
    # a simple password decryption method, better better and better to keep it safe
    dec_secret = AES.new(Config.MASTER_KEY)
    raw_decrypted = dec_secret.decrypt(base64.b64decode(cipher_text))
    clear_text = raw_decrypted.decode('utf-8').rstrip("\0")
    return clear_text
