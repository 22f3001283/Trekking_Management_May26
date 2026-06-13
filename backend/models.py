from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()


class UserRole:
    ADMIN = "admin"
    STAFF = "staff"
    USER  = "user"

class UserStatus:
    ACTIVE      = "active"
    BLACKLISTED = "blacklisted"
    INACTIVE    = "inactive"

class TrekDifficulty:
    EASY     = "Easy"
    MODERATE = "Moderate"
    HARD     = "Hard"

class TrekStatus:
    PENDING   = "Pending"
    APPROVED  = "Approved"
    OPEN      = "Open"
    CLOSED    = "Closed"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class BookingStatus:
    BOOKED    = "Booked"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"

class PaymentStatus:
    PENDING = "Pending"
    PAID    = "Paid"
    FAILED  = "Failed"


# -------------------------------------------------------------------
# USER
# -------------------------------------------------------------------

class User(db.Model):
    __tablename__ = "user"

    user_id      = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username     = db.Column(db.String(100), nullable=False)
    email        = db.Column(db.String(150), unique=True, nullable=False)
    password_hash= db.Column(db.String(256), nullable=False)
    role         = db.Column(db.String(10),  nullable=False)
    contact      = db.Column(db.String(20),  nullable=True)
    status       = db.Column(db.String(20),  default="inactive",  nullable=True)         
    rating       = db.Column(db.Float,       nullable=True)
    created_at   = db.Column(db.DateTime,    default=datetime.utcnow)

    # Relationships
    bookings     = db.relationship("Booking", back_populates="user",
                                   foreign_keys="Booking.user_id",
                                   lazy="dynamic", cascade="all, delete-orphan")
    reviews      = db.relationship("Review",  back_populates="user",
                                   lazy="dynamic", cascade="all, delete-orphan")
    assigned_treks = db.relationship("Trek",  back_populates="assigned_staff",
                                     foreign_keys="Trek.assigned_staff_id",
                                     lazy="dynamic")

    def serialize(self):
        return {
            "user_id"   : self.user_id,
            "username"  : self.username,
            "email"     : self.email,
            "role"      : self.role,
            "contact"   : self.contact,
            "status"    : self.status,
            "rating"    : self.rating,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


# -------------------------------------------------------------------
# TREK
# -------------------------------------------------------------------

class Trek(db.Model):
    __tablename__ = "trek"

    trek_id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    trek_name        = db.Column(db.String(150), nullable=False)
    location         = db.Column(db.String(150), nullable=False)
    difficulty       = db.Column(db.String(10),  nullable=False)
    duration_days    = db.Column(db.Integer,     nullable=False)
    available_slots  = db.Column(db.Integer,     nullable=False)
    price            = db.Column(db.Float,       nullable=False, default=0.0)  # price per person
    assigned_staff_id= db.Column(db.Integer, db.ForeignKey("user.user_id", ondelete="SET NULL"),
                                 nullable=True)
    status           = db.Column(db.String(20),  nullable=False, default=TrekStatus.PENDING)
    start_date       = db.Column(db.Date,  nullable=False)
    end_date         = db.Column(db.Date,  nullable=False)
    _images          = db.Column("images", db.Text, nullable=True, default="[]")
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    assigned_staff   = db.relationship("User", back_populates="assigned_treks",
                                       foreign_keys=[assigned_staff_id])
    bookings         = db.relationship("Booking", back_populates="trek", lazy="dynamic",
                                       cascade="all, delete-orphan")
    reviews          = db.relationship("Review",  back_populates="trek", lazy="dynamic",
                                       cascade="all, delete-orphan")

    @property
    def average_rating(self):
        all_reviews = self.reviews.all()
        if not all_reviews:
            return None
        return round(sum(r.rating for r in all_reviews) / len(all_reviews), 2)

    @property
    def images(self):
        try:
            return json.loads(self._images or "[]")
        except (json.JSONDecodeError, TypeError):
            return []

    @images.setter
    def images(self, file_paths: list):
        self._images = json.dumps(file_paths)

    def serialize(self):
        return {
            "trek_id"          : self.trek_id,
            "trek_name"        : self.trek_name,
            "location"         : self.location,
            "difficulty"       : self.difficulty,
            "duration_days"    : self.duration_days,
            "available_slots"  : self.available_slots,
            "price"            : self.price,
            "assigned_staff_id": self.assigned_staff_id,
            "assigned_staff_name": self.assigned_staff.username if self.assigned_staff else None,
            "status"           : self.status,
            "start_date"       : self.start_date.isoformat() if self.start_date else None,
            "end_date"         : self.end_date.isoformat() if self.end_date else None,
            "created_at"       : self.created_at.isoformat() if self.created_at else None,
            "average_rating"   : self.average_rating,
            "images"           : self.images if len(self.images)>0 else ["src/assets/TrekDefault.png"]
        }


# -------------------------------------------------------------------
# BOOKING
# -------------------------------------------------------------------

class Booking(db.Model):
    __tablename__ = "booking"

    # Unique constraint: one booking per user per trek
    __table_args__ = (
        db.UniqueConstraint("user_id", "trek_id", name="uq_user_trek_booking"),
    )

    booking_id     = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id        = db.Column(db.Integer, db.ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    trek_id        = db.Column(db.Integer, db.ForeignKey("trek.trek_id", ondelete="CASCADE"), nullable=False)
    booking_date   = db.Column(db.DateTime, default=datetime.utcnow)
    status         = db.Column(db.String(20), nullable=False, default=BookingStatus.BOOKED)
    payment_status = db.Column(db.String(20), nullable=False, default=PaymentStatus.PENDING)

    # Relationships
    user         = db.relationship("User", back_populates="bookings", foreign_keys=[user_id])
    trek         = db.relationship("Trek", back_populates="bookings")
    participants = db.relationship("Participant", back_populates="booking",
                                   lazy="dynamic", cascade="all, delete-orphan")

    @property
    def num_people(self):
        """Derive participant count instead of storing it separately."""
        return self.participants.count()

    def serialize(self):
        return {
            "booking_id"    : self.booking_id,
            "user_id"       : self.user_id,
            "trek_id"       : self.trek_id,
            "booking_date"  : self.booking_date.isoformat() if self.booking_date else None,
            "num_people"    : self.num_people,
            "status"        : self.status,
            "payment_status": self.payment_status
        }


# -------------------------------------------------------------------
# PARTICIPANT
# -------------------------------------------------------------------

class Participant(db.Model):
    __tablename__ = "participant"

    participant_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    booking_id     = db.Column(db.Integer, db.ForeignKey("booking.booking_id", ondelete="CASCADE"), nullable=False)
    name           = db.Column(db.String(100), nullable=False)
    dob            = db.Column(db.Date,        nullable=False)
    aadhar         = db.Column(db.String(12),  nullable=False, unique=True)  # 12-digit Aadhar

    # Relationships
    booking = db.relationship("Booking", back_populates="participants")

    def serialize(self):
        return {
            "participant_id": self.participant_id,
            "booking_id"    : self.booking_id,
            "name"          : self.name,
            "dob"           : self.dob.isoformat() if self.dob else None,
            "aadhar"        : self.aadhar
        }


# -------------------------------------------------------------------
# REVIEW
# -------------------------------------------------------------------

class Review(db.Model):
    __tablename__ = "review"

    # Unique constraint: one review per user per trek
    __table_args__ = (
        db.UniqueConstraint("user_id", "trek_id", name="uq_user_trek_review"),
    )

    review_id   = db.Column(db.Integer, primary_key=True, autoincrement=True)
    trek_id     = db.Column(db.Integer, db.ForeignKey("trek.trek_id", ondelete="CASCADE"), nullable=False)
    user_id     = db.Column(db.Integer, db.ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    rating      = db.Column(db.Integer, nullable=False)              # 1–5
    comment     = db.Column(db.Text,    nullable=True)
    _attachments= db.Column("attachments", db.Text, nullable=True, default="[]")
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship("User", back_populates="reviews")
    trek = db.relationship("Trek", back_populates="reviews")

    @property
    def attachments(self):
        try:
            return json.loads(self._attachments or "[]")
        except (json.JSONDecodeError, TypeError):
            return []

    @attachments.setter
    def attachments(self, file_paths: list):
        self._attachments = json.dumps(file_paths)

    def add_attachment(self, file_path: str):
        current = self.attachments
        current.append(file_path)
        self.attachments = current

    def serialize(self):
        return {
            "review_id" : self.review_id,
            "trek_id"   : self.trek_id,
            "user_id"   : self.user_id,
            "rating"    : self.rating,
            "comment"   : self.comment,
            "attachments": self.attachments,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


# -------------------------------------------------------------------
# DB initialisation helper
# -------------------------------------------------------------------

def init_db(app):
    from werkzeug.security import generate_password_hash

    db.init_app(app)

    with app.app_context():
        db.create_all()

        admin = User.query.filter_by(role=UserRole.ADMIN).first()
        if not admin:
            admin = User(
                username      = "admin",
                email         = "admin@tma.com",
                password_hash = generate_password_hash("admin123"),  
                role          = UserRole.ADMIN,
                contact       = None,
                status        = "active",
                rating        = None,
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user seeded.")
        else:
            print("Admin already exists, skipping seed.")