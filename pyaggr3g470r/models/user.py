#! /usr/bin/env python
# -*- coding: utf-8 -*-

# pyAggr3g470r - A Web based news aggregator.
# Copyright (C) 2010-2015  Cédric Bonhomme - https://www.cedricbonhomme.org
#
# For more information : https://bitbucket.org/cedricbonhomme/pyaggr3g470r/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "Cedric Bonhomme"
__version__ = "$Revision: 0.4 $"
__date__ = "$Date: 2013/11/05 $"
__revision__ = "$Date: 2014/04/12 $"
__copyright__ = "Copyright (c) Cedric Bonhomme"
__license__ = "GPLv3"

import re
import random
import hashlib
from datetime import datetime
from flask import g
from werkzeug import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin

db = g.db


class User(db.Model, UserMixin):
    """
    Represent a user.
    """
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(), unique=True)
    email = db.Column(db.String(254), index=True, unique=True)
    pwdhash = db.Column(db.String())
    roles = db.relationship('Role', backref='user', lazy='dynamic')
    activation_key = db.Column(db.String(128), default=hashlib.sha512(
            str(random.getrandbits(256)).encode("utf-8")).hexdigest()[:86])
    date_created = db.Column(db.DateTime(), default=datetime.now)
    last_seen = db.Column(db.DateTime(), default=datetime.now)
    feeds = db.relationship('Feed', backref='subscriber', lazy='dynamic',
                            cascade='all,delete-orphan')
    refresh_rate = db.Column(db.Integer, default=60)  # in minutes

    @staticmethod
    def make_valid_nickname(nickname):
        return re.sub('[^a-zA-Z0-9_\.]', '', nickname)

    def get_id(self):
        """
        Return the id (email) of the user.
        """
        return self.email

    def set_password(self, password):
        """
        Hash the password of the user.
        """
        self.pwdhash = generate_password_hash(password)

    def check_password(self, password):
        """
        Check the password of the user.
        """
        return check_password_hash(self.pwdhash, password)

    def is_admin(self):
        """
        Return True if the user has administrator rights.
        """
        return len([role for role in self.roles if role.name == "admin"]) != 0

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return '<User %r>' % (self.nickname)
