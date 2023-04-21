# -*- coding: utf-8 -*-
"""User models."""
import datetime as dt

from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property

from riddle_me_this.database import Column, PkModel, db, reference_col, relationship
from riddle_me_this.extensions import bcrypt


class Role(PkModel):
    """A role for a user."""

    __tablename__ = "roles"
    name = Column(db.String(80), unique=True, nullable=False)
    user_id = reference_col("users", nullable=True)
    user = relationship("User", backref="roles")

    def __init__(self, name, **kwargs):
        """Create instance."""
        super().__init__(name=name, **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return f"<Role({self.name})>"


class User(UserMixin, PkModel):
    """A user of the app."""

    __tablename__ = "users"
    username = Column(db.String(80), unique=True, nullable=False)
    email = Column(db.String(80), unique=True, nullable=False)
    _password = Column("password", db.LargeBinary(128), nullable=True)
    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    first_name = Column(db.String(30), nullable=True)
    last_name = Column(db.String(30), nullable=True)
    active = Column(db.Boolean(), default=False)
    is_admin = Column(db.Boolean(), default=False)

    @hybrid_property
    def password(self):
        """Hashed password."""
        return self._password

    @password.setter
    def password(self, value):
        """Set password."""
        self._password = bcrypt.generate_password_hash(value)

    def check_password(self, value):
        """Check password."""
        return bcrypt.check_password_hash(self._password, value)

    @property
    def full_name(self):
        """Full user name."""
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        """Represent instance as a unique string."""
        return f"<User({self.username!r})>"


class Transcript(PkModel):
    """A transcript for a video."""

    __tablename__ = "transcripts"
    video_id = Column(db.String, nullable=True)
    json_string = Column(db.Text, nullable=True)
    text = Column(db.Text, nullable=True)
    language_code = Column(db.String(10), nullable=True)
    is_generated = Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        """Represent instance as a unique string."""
        return f"<Transcript({self.language_code}-{self.id})>"


class Video(PkModel):
    """A video record."""

    __tablename__ = "videos"
    video_id = Column(db.String, nullable=True)
    snippet_published_at = Column(db.DateTime, nullable=True)
    snippet_channel_id = Column(db.String, nullable=True)
    snippet_title = Column(db.String, nullable=True)
    snippet_description = Column(db.Text, nullable=True)
    snippet_channel_title = Column(db.String, nullable=True)
    snippet_category_id = Column(db.String, nullable=True)
    snippet_thumbnails_maxres_url = Column(db.String, nullable=True)
    content_details_definition = Column(db.String, nullable=True)
    content_details_licensed_content = Column(db.Boolean, nullable=True)
    status_upload_status = Column(db.String, nullable=True)
    status_privacy_status = Column(db.String, nullable=True)
    status_license = Column(db.String, nullable=True)
    status_public_stats_viewable = Column(db.Boolean, nullable=True)
    status_made_for_kids = Column(db.Boolean, nullable=True)
    statistics_view_count = Column(db.Integer, nullable=True)
    statistics_like_count = Column(db.Integer, nullable=True)
    statistics_favorite_count = Column(db.Integer, nullable=True)
    statistics_comment_count = Column(db.Integer, nullable=True)

    def __repr__(self):
        """Represent instance as a unique string."""
        return f"<Video({self.snippet_title!r}-{self.id})>"
