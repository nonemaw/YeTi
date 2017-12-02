""" this file stores methods for a general access across the application
"""
import bleach
import random
import string
from markdown import markdown
from threading import Thread
from flask import current_app, render_template, request
from flask_mail import Message
from werkzeug.security import check_password_hash

from app import mail
from app.db import mongo_connect, client


def get_company_list():
    db = mongo_connect(client, 'ytml')
    companies = db.Company.find({}).sort([('name', 1)])
    company_list = []
    for company_dict in companies:
        company_list.append(company_dict.get('name'))
    return company_list


def verify_password(password_hash: str, password: str):
    return check_password_hash(password_hash, password)


def send_async_email(app, msg: str):
    with app.app_context():
        mail.send(msg)


def send_email(to: str, subject: str, template: str, **kwargs) -> Thread:
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


def gravatar(avatar_hash: str, size: int = 100, default: str = 'identicon',
             rating: str = 'g') -> str:
    if request.is_secure:
        url = 'https://secure.gravatar.com/avatar'
    else:
        url = 'http://www.gravatar.com/avatar'
    return '{u}/{h}?s={s}&d={d}&r={r}'.format(u=url, h=avatar_hash, s=size,
                                              d=default, r=rating)


def clean_tags(body: str) -> str:
    allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                    'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul', 'h1',
                    'h2', 'h3', 'p']
    return bleach.linkify(bleach.clean(markdown(body, output_format='html'),
                                       tags=allowed_tags, strip=True))


def random_word(size: int = 8,
                chars: str = string.ascii_uppercase + string.digits) -> str:
    return ''.join(random.choice(chars) for _ in range(size))
