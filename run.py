from app import create_app

app = create_app()
app.template_folder = 'templates'

if __name__ == '__main__':
    app.run(debug=True)