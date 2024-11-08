# point d'entree de l'application 

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run()