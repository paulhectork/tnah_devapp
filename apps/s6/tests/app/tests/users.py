

# app/tests/test_config.py
def test_uses_memory_db_in_testing(app):
    """Verify testing mode uses in-memory database."""
    assert app.config["TESTING"] is True
    assert "memory" in str(app.config["SQLALCHEMY_DATABASE_URI"])

def test_is_testing_mode(app):
    """Verify we're in testing mode."""
    with app.app_context():
        # Database should be empty on each test
        from app.models import User  # Import your model
        count = db.session.query(User).count()
        assert count == 0