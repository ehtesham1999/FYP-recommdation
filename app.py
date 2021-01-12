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



item_similarity_df = load_recommendations()
product_ratings = load_products()
#item_similarity_df = cache.ram('item_similarity_df3', load_recommendations, None)
# print(item_similarity_df.head())
def prod_name(prodid):
    return product_ratings.loc[product_ratings['prod_ID'] == prodid ].iloc[0]['prod_name']

def prod_img(prodid):
    return product_ratings.loc[product_ratings['prod_ID'] == prodid ].iloc[0]['imgurl']

def get_similar_products(prod_name, user_rating):
    try:
        similar_score = item_similarity_df[prod_name] * (user_rating - 2.5)
        similar_prods = similar_score.sort_values(ascending=False)
    except:
        print("don't have product in model")
        similar_prods = pd.Series([])

    return similar_prods


@app.route('/getdata', methods=['POST'])
def get_autocomplete_data():
    return product_ratings.to_json(orient='records')



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

