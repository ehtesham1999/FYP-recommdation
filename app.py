from flask import Flask
import pandas as pd
from flask import request
app = Flask(__name__)



@app.route('/postjson', methods=['POST'])
def postJsonHandler():
    # print(request.is_json)
    content = request.get_json()
    a = content['name']
    b = content['dept']
    # print("got: ", a, b)
    result = a + b
    return dict(result=result, status="success")



@app.route('/')
def hello_world():
    return 'Hello World!'

def load_recommendations():
    item_similarity_df = pd.read_csv("static/item_similarity_df.csv", index_col=0)
    print("item_similarity_df cached in memory")
    return item_similarity_df


item_similarity_df = load_recommendations()
# item_similarity_df = cache.ram('item_similarity_df3', load_recommendations, None)
# print(item_similarity_df.head())


def get_similar_movies(movie_name, user_rating):
    try:
        similar_score = item_similarity_df[movie_name] * (user_rating - 2.5)
        similar_movies = similar_score.sort_values(ascending=False)
    except:
        print("don't have movie in model")
        similar_movies = pd.Series([])

    return similar_movies


def check_seen(recommended_movie, watched_movies):
    for movie_id, movie in watched_movies.items():
        movie_title = movie["title"]

        if recommended_movie == movie_title:
            return True

    return False



@app.route('/getrecommendations', methods=['POST'])
def get_recommendations():
    content = request.get_json()
    watched_movies = content["watched_movies"]
    similar_movies = pd.DataFrame()

    for movie_id, movie in watched_movies.items():
        similar_movies = similar_movies.append(get_similar_movies(movie["title"], movie["rating"]), ignore_index=True)

    all_recommend = similar_movies.sum().sort_values(ascending=False)

    recommended_movies = []
    for movie, score in all_recommend.iteritems():
        if not check_seen(movie, watched_movies):
            recommended_movies.append(movie)

    if len(recommended_movies) > 100:
        recommended_movies = recommended_movies[0:100]

    print(recommended_movies)
    return dict({"recommm":recommended_movies})
    #return None




if __name__ == '__main__':
    app.run()

