from db.database import Database
from cli.menu import run_menu


def main():
    db = Database(
        host="localhost",
        port=5432,
        database="veterinary_clinic",
        user="postgres",
        password="10451045"
    )
    
    db.connect()

    try:
        run_menu(db) # запуск главного меню
    finally:
        db.close()


if __name__ == "__main__":
    main()
