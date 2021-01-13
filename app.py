from flask import Flask
import pandas as pd
from flask import request
app = Flask(__name__)

# {"all_products": {
#     "1400532655": {
#         "prodId": "1400532655",
#         "rating": 5
#     }
#     ,
#
#     "B001NJ0D0Y": {
#         "prodId": "B001NJ0D0Y",
#         "rating": 3
#     }
#
# }
# }

nb_closest_images = 5


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
    item_similarity_df = pd.read_csv("static/prod_similarity.csv", index_col=0)
    print("item_similarity_df cached in memory")
    return item_similarity_df
def load_products():
    product_ratings = pd.read_csv("static/prod_ratings.csv")
    return product_ratings

def load_images():
    images = pd.read_csv('static/img_similarity.csv',index_col=0)
    return images

item_similarity_df = load_recommendations()
product_ratings = load_products()
cos_similarities_df = load_images()
#item_similarity_df = cache.ram('item_similarity_df3', load_recommendations, None)
# print(item_similarity_df.head())
def prod_name(prodid):
    return product_ratings.loc[product_ratings['prod_ID'] == prodid ].iloc[0]['prod_name']

def prod_img(prodid):
    return product_ratings.loc[product_ratings['prod_ID'] == prodid ].iloc[0]['imgurl']


# function to retrieve the most similar products for a given one
@app.route('/getsimilarimage', methods=['POST'])
def retrieve_most_similar_products():
    content = request.get_json()
    given_img = content['prod_ID']
    print("-----------------------------------------------------------------------")
    print("original product:")
    print(given_img)



    print("-----------------------------------------------------------------------")
    print("most similar products:")

    closest_imgs = cos_similarities_df[given_img].sort_values(ascending=False)[1:nb_closest_images + 1].index
    closest_imgs_scores = cos_similarities_df[given_img].sort_values(ascending=False)[1:nb_closest_images + 1]

    print(closest_imgs)
    print(closest_imgs_scores)
    data = {'prod_ID': closest_imgs,
            'scores': closest_imgs_scores}
    img_df = pd.DataFrame(data)

    img_df['imgurl'] = img_df['prod_ID'].apply(prod_img)
    img_df['prodname'] = img_df['prod_ID'].apply(prod_name)

    # for i in range(0, len(closest_imgs)):
    #     print(closest_imgs[i])
    #     print('score :'+closest_imgs_scores[i])

    #return dict({"lst":closest_imgs})
    return img_df.to_json(orient='records')

def get_similar_products(prod_name, user_rating):
    try:
        similar_score = item_similarity_df[prod_name] * (user_rating - 2.5)
        similar_prods = similar_score.sort_values(ascending=False)
    except:
        print("don't have product in model")
        similar_prods = pd.Series([])

    return similar_prods


@app.route('/getdata', methods=['GET'])
def get_autocomplete_data():
    return product_ratings.to_json(orient='index')

@app.route('/getpopular', methods=['GET'])
def getpopular():
    ratings_sum = pd.DataFrame(product_ratings.groupby(['prod_ID'])['rating'].sum()).rename(columns={'rating': 'ratings_sum'})
    top10 = ratings_sum.sort_values('ratings_sum', ascending=False).head(10)

    top10_popular = top10.merge(product_ratings, left_index=True, right_on='prod_ID').drop_duplicates(
        ['prod_ID', 'prod_name'])[['prod_ID', 'prod_name', 'ratings_sum']]
    top10_popular['imgurl'] = top10_popular['prod_ID'].apply(prod_img)
    return top10_popular.to_json(orient='records')

def check_seen(recommended_product, all_products):
    for prod_id, product in all_products.items():
        prod_title = product["prodId"]

        if recommended_product == prod_title:
            return True

    return False



@app.route('/getrecommendations', methods=['POST'])
def get_recommendations():
    content = request.get_json()
    all_products = content["all_products"]
    similar_products = pd.DataFrame()

    for proid_id, product in all_products.items():
        print(product["prodId"], product["rating"])
        similar_items = similar_products.append(get_similar_products(product["prodId"], product["rating"]), ignore_index=True)


    #all_recommend = similar_items.sum().sort_values(ascending=False)

    final_results = pd.DataFrame(similar_items.sum().sort_values(ascending=False).head(20))
    final_results.reset_index(inplace=True)
    final_results.columns = ['prodid', 'rating']
    final_results['prodname'] = final_results['prodid'].apply(prod_name)
    final_results['imgurl'] = final_results['prodid'].apply(prod_img)



    return final_results.to_json(orient='records')


    # recommended_prods = []
    # for prod, score in all_recommend.iteritems():
    #     if not check_seen(prod, all_products):
    #         recommended_prods.append(prod)
    #
    # recon_prods = {}
    # for i in range(len(recommended_prods)):
    #     recon_prods['']prod_name(recommended_prods[i])
    #
    # if len(recommended_prods) > 100:
    #     recommended_prods = recommended_prods[0:100]
    #
    # print(recommended_prods)
    # #return dict({"recommm":recommended_movies})
    # json = dataFrame.to_json()
    # return dict({"hello":"world"})

if __name__ == '__main__':
    app.run()

