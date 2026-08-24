def test_sqlite_foreign_keys_are_enabled(
    app,
):
    from models.article import db

    with app.app_context():
        value = (
            db.session
            .connection()
            .exec_driver_sql(
                "PRAGMA foreign_keys"
            )
            .scalar()
        )

    assert value == 1