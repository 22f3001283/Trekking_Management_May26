from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
 
db = SQLAlchemy()

 
# -------------------------------------------------------------------
# Enums (as plain string constants — SQLite doesn't support native ENUMs)
# -------------------------------------------------------------------
 
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
    name         = db.Column(db.String(100), nullable=True)          # null for admin
    email        = db.Column(db.String(150), unique=True, nullable=False)
    password_hash= db.Column(db.String(256), nullable=False)
    role         = db.Column(db.String(10),  nullable=False)         # admin / staff / user
    contact      = db.Column(db.String(20),  nullable=True)          # null for admin
    status       = db.Column(db.String(20),  nullable=True)          # null for admin
    rating       = db.Column(db.Float,       nullable=True)          # null for admin
    created_at   = db.Column(db.DateTime,    default=datetime.utcnow)
 
    # Relationships
    bookings     = db.relationship("Booking", back_populates="user",
                                   foreign_keys="Booking.user_id",
                                   lazy="dynamic", cascade="all, delete-orphan")
    reviews      = db.relationship("Review",  back_populates="user",  lazy="dynamic", cascade="all, delete-orphan")
    assigned_treks = db.relationship("Trek",  back_populates="assigned_staff",
                                     foreign_keys="Trek.assigned_staff_id",
                                     lazy="dynamic")
 
    def __repr__(self):
        return f"<User {self.user_id} | {self.role} | {self.email}>"
 
 
# -------------------------------------------------------------------
# TREK
# -------------------------------------------------------------------
 
class Trek(db.Model):
    __tablename__ = "trek"
 
    trek_id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    trek_name        = db.Column(db.String(150), nullable=False)
    location         = db.Column(db.String(150), nullable=False)
    difficulty       = db.Column(db.String(10),  nullable=False)     # Easy / Moderate / Hard
    duration_days    = db.Column(db.Integer,      nullable=False)
    available_slots  = db.Column(db.Integer,      nullable=False)
    assigned_staff_id= db.Column(db.Integer, db.ForeignKey("user.user_id", ondelete="SET NULL"),
                                 nullable=True)                       # FK → User (role=staff)
    status           = db.Column(db.String(20),  nullable=False,
                                 default=TrekStatus.PENDING)
    start_date       = db.Column(db.Date, nullable=False)
    end_date         = db.Column(db.Date, nullable=False)
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)
 
    # Relationships
    assigned_staff   = db.relationship("User", back_populates="assigned_treks",
                                       foreign_keys=[assigned_staff_id])
    bookings         = db.relationship("Booking", back_populates="trek", lazy="dynamic", cascade="all, delete-orphan")
    reviews          = db.relationship("Review",  back_populates="trek", lazy="dynamic", cascade="all, delete-orphan")
 
    @property
    def average_rating(self):
        """Compute average rating from reviews on the fly — no stored column needed."""
        all_reviews = self.reviews.all()
        if not all_reviews:
            return None
        return round(sum(r.rating for r in all_reviews) / len(all_reviews), 2)
 
    def __repr__(self):
        return f"<Trek {self.trek_id} | {self.trek_name} | {self.status}>"
 
 
# -------------------------------------------------------------------
# BOOKING
# -------------------------------------------------------------------
 
class Booking(db.Model):
    __tablename__ = "booking"
 
    # Unique constraint: one booking per user per trek (no duplicates)
    __table_args__ = (
        db.UniqueConstraint("user_id", "trek_id", name="uq_user_trek_booking"),
    )
 
    booking_id     = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id        = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    trek_id        = db.Column(db.Integer, db.ForeignKey("trek.trek_id"), nullable=False)
    booking_date   = db.Column(db.DateTime, default=datetime.utcnow)
    num_people     = db.Column(db.Integer, nullable=False, default=1)
    status         = db.Column(db.String(20), nullable=False, default=BookingStatus.BOOKED)
    payment_status = db.Column(db.String(20), nullable=False, default=PaymentStatus.PENDING)
 
    # Relationships
    user = db.relationship("User", back_populates="bookings", foreign_keys=[user_id])
    trek = db.relationship("Trek", back_populates="bookings")
 
    def __repr__(self):
        return f"<Booking {self.booking_id} | User {self.user_id} | Trek {self.trek_id}>"
 
 
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
    trek_id     = db.Column(db.Integer, db.ForeignKey("trek.trek_id"), nullable=False)
    user_id     = db.Column(db.Integer, db.ForeignKey("user.user_id"), nullable=False)
    rating      = db.Column(db.Integer, nullable=False)              # 1–5
    comment     = db.Column(db.Text,    nullable=True)
    # Stored as JSON array string: '["/uploads/abc.jpg", "/uploads/xyz.mp4"]'
    _attachments= db.Column("attachments", db.Text, nullable=True, default="[]")
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
 
    # Relationships
    user = db.relationship("User", back_populates="reviews")
    trek = db.relationship("Trek", back_populates="reviews")
 
    # --- Attachment helpers ---
 
    @property
    def attachments(self):
        """Return attachments as a Python list."""
        try:
            return json.loads(self._attachments or "[]")
        except (json.JSONDecodeError, TypeError):
            return []
 
    @attachments.setter
    def attachments(self, file_paths: list):
        """Accept a list of file path strings and serialise to JSON."""
        self._attachments = json.dumps(file_paths)
 
    def add_attachment(self, file_path: str):
        current = self.attachments
        current.append(file_path)
        self.attachments = current
 
    def __repr__(self):
        return f"<Review {self.review_id} | User {self.user_id} | Trek {self.trek_id} | Rating {self.rating}>"
 
 
# -------------------------------------------------------------------
# DB initialisation helper--> in app.py 
# -------------------------------------------------------------------
 
def init_db(app):
    """
    Call this once at app startup.
    Creates all tables and seeds the admin user if not present.
    """
    from werkzeug.security import generate_password_hash
 
    db.init_app(app)
 
    with app.app_context():
        db.create_all()
 
        # Seed admin (only if not already present)
        admin = User.query.filter_by(role=UserRole.ADMIN).first()
        if not admin:
            admin = User(
                name          = None,
                email         = "admin@tma.com",
                password_hash = generate_password_hash("admin123"),  # change in prod
                role          = UserRole.ADMIN,
                contact       = None,
                status        = None,
                rating        = None,
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user seeded.")
        else:
            print("ℹ️  Admin already exists, skipping seed.")
 