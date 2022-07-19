from flask import Flask, request
from flask_restx import Api, Resource
from marshmallow import ValidationError
from flask_restx.representations import output_json
from models import *
from schema import *

app = Flask(__name__)
app.config.from_pyfile('config.py')
db.init_app(app)

api = Api(app)
api.representations = {'application/json; charset=utf-8': output_json}
movies_ns = api.namespace('movies')
directors_ns = api.namespace('directors')
genres_ns = api.namespace('genres')

movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)
director_schema = DirectorSchema()
genre_schema = GenreSchema()


@movies_ns.route('/')
class MoviesView(Resource):

    def get(self):

        director_id = request.args.get('director_id', type=int)
        genre_id = request.args.get('genre_id', type=int)

        if director_id and genre_id:
            movies_found = db.session.query(
                Movie.id,
                Movie.title,
                Movie.description,
                Movie.trailer,
                Movie.rating,
                Genre.name.label('genre'),
                Director.name.label('director')) \
                .join(Movie.genre) \
                .join(Movie.director) \
                .filter(Movie.genre_id == genre_id, Movie.director_id == director_id) \
                .all()
            if not movies_found:
                return f"Не найдены фильмы с director_id: {director_id}" \
                       f" и genre_id: {genre_id}", 204
            else:
                return movies_schema.dump(movies_found), 200

        if director_id:
            movies_found = db.session.query(
                Movie.id,
                Movie.title,
                Movie.description,
                Movie.trailer,
                Movie.rating,
                Genre.name.label('genre'),
                Director.name.label('director')) \
                .join(Movie.genre) \
                .join(Movie.director) \
                .filter(Movie.director_id == director_id) \
                .all()
            if not movies_found:
                return f"Не найдены фильмы с director_id: {director_id}", 204
            else:
                return movies_schema.dump(movies_found), 200

        if genre_id:
            movies_found = db.session.query(
                Movie.id,
                Movie.title,
                Movie.description,
                Movie.trailer,
                Movie.rating,
                Genre.name.label('genre'),
                Director.name.label('director')) \
                .join(Movie.genre) \
                .join(Movie.director) \
                .filter(Movie.genre_id == genre_id) \
                .all()
            if not movies_found:
                return f"Не найдены фильмы с genre_id: {genre_id}", 204
            else:
                return movies_schema.dump(movies_found), 200

        else:
            movies_all = db.session.query(
                Movie.id,
                Movie.title,
                Movie.description,
                Movie.trailer,
                Movie.rating,
                Genre.name.label('genre'),
                Director.name.label('director')) \
                .join(Movie.genre) \
                .join(Movie.director) \
                .all()
            return movies_schema.dump(movies_all), 200


@movies_ns.route('/<int:uid>')
class MovieView(Resource):

    def get(self, uid):
        movie_uid = Movie.query.get(uid)
        return movie_schema.dump(movie_uid), 200


@directors_ns.route('/')
class DirectorsView(Resource):

    def post(self):

        try:
            data = request.json
            director = Director(**director_schema.load(data))

        except ValidationError as e:
            return f"{e}", 400

        else:
            with db.session.begin():
                db.session.add(director)
            return "Данные добавлены", 201


@directors_ns.route('/<int:uid>')
class DirectorView(Resource):

    def get(self, uid):

        director = Director.query.get(uid)
        db.session.close()

        if not director:
            return f"Режиссер с id: {uid} не найден", 404
        else:
            return director_schema.dump(director), 200

    def put(self, uid):

        try:
            data = director_schema.load(request.json)
            director = Director.query.get(uid)

            if not director:
                return f"Жанр с id: {uid} не найден", 404

        except ValidationError as e:
            return f"{e}", 400

        else:
            director.name = data['name']
            db.session.commit()
            db.session.close()
            return f"Данные режиссера с id: {uid} обновлены", 201

    def delete(self, uid):
        director = Director.query.get(uid)

        if not director:
            return f"Режиссер с id: {uid} не найден", 404

        else:
            db.session.delete(director)
            db.session.commit()
            db.session.close()
            return f"Режиссер с id: {uid} удален", 201


@genres_ns.route('/')
class GenresView(Resource):

    def post(self):

        try:
            data = request.json
            genre = Genre(**genre_schema.load(data))

        except ValidationError as e:
            return f"{e}", 400

        else:
            with db.session.begin():
                db.session.add(genre)
            return "Данные добавлены", 201


@genres_ns.route('/<int:uid>')
class GenreView(Resource):

    def get(self, uid):

        genre = Genre.query.get(uid)
        db.session.close()

        if not genre:
            return f"Жанр с id: {uid} не найден", 404
        else:
            return genre_schema.dump(genre), 200

    def put(self, uid):

        try:
            data = genre_schema.load(request.json)
            genre = Genre.query.get(uid)

            if not genre:
                return f"Жанр с id: {uid} не найден", 404

        except ValidationError as e:
            return f"{e}", 400

        else:
            genre.name = data['name']
            db.session.commit()
            db.session.close()
            return f"Данные жанра с id: {uid} обновлены", 201

    def delete(self, uid):
        genre = Genre.query.get(uid)
        if not genre:
            return f"Жанр с id: {uid} не найден", 404
        else:
            db.session.delete(genre)
            db.session.commit()
            db.session.close()
            return f"Данные жанра с id: {uid} удалены", 201


if __name__ == '__main__':
    app.run()
