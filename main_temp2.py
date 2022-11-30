import functions_framework
#using nltk to do sentimental analysis
import pandas as pd
import nltk

nltk.download(["names",
"stopwords",
"state_union",
"twitter_samples",
"movie_reviews",
"averaged_perceptron_tagger",
"vader_lexicon","punkt"], download_dir='review_analysis_v1_tempfiles')
from nltk.stem.porter import PorterStemmer
# library to clean data
import re
from nltk.corpus import stopwords
from nltk.corpus import state_union
from nltk.tokenize import PunktSentenceTokenizer

import string

import warnings 
from nltk.sentiment import SentimentIntensityAnalyzer
sia = SentimentIntensityAnalyzer()
warnings.filterwarnings("ignore", category=DeprecationWarning)
@functions_framework.http


def filter(rvw):
    sw=[]
    sw = list(stopwords.words('english'))
    sw.remove("no")
    sw.append("pm")
    sw.append("am")
    try:
        rvw = re.sub('[^a-zA-Z]', ' ', rvw)
        # convert all cases to lower cases
        rvw = rvw.lower()
        rvw = nltk.word_tokenize(rvw)
        ps = PorterStemmer()
        # review = [ps.stem(word) for word in review
        #           if not word in set(stopwords.words('english'))]
        rvw = [word for word in rvw
                  if not word in sw]

        tagged = nltk.pos_tag(rvw)
        grammar = "NP: {<JJ.?>*<NN>+<NNP>?}"
        # grammar = "NP: {<JJ.?>*<NN.?>}"
        # grammar = "NP: {<RB.?>*<JJ.?>*<NN.?>}"
        cp = nltk.RegexpParser(grammar)
        rvw = cp.parse(tagged)
        rslt = ""
        for subtree in rvw.subtrees(filter=lambda t: t.label() == 'NP'):
            leaves = subtree.leaves()

            for i in leaves:
                rslt += i[0]
                rslt += " "
            # namedEnt.draw()
            return rslt
        # neutral_word_cloud += result

    except Exception as e:
        print(str(e))
        return
def reviews_analysis_v1(request):
    """HTTP Clpy -m pip install --upgrade pipoud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    Note:
        For more information on how Flask integrates with Cloud
        Functions, see the `Writing HTTP functions` page.
        <https://cloud.google.com/functions/docs/writing/http#http_frameworks>
    """
    request_data = request.get_json()
    restaurant__reviews = request_data["reviews"]
    # sent_pipeline = pipeline("sentiment-analysis")
    pros = []
    neutral = []
    cons = []

    pros_word_cloud = []
    cons_word_cloud = []
    neutral_word_cloud = []
    


    
  
    for i in range(0, len(restaurant__reviews)):
        # text = df["Text"][i]
     text = restaurant__reviews[i]
     try:
        scoreObj = sia.polarity_scores(text)

        if scoreObj['compound'] >0.90:
           if scoreObj['pos'] >0.5:
                pros.append(text)
           else:
                neutral.append(text)
        elif scoreObj['neg'] >0:
            cons.append(text)

     except Exception:
        print("error in sentiment analysis")
        return "Error in sentiment analysis", 500
    print("***************Pros:************** ")
    print(pros)
    for review in pros:
         result = filter(review)
         pros_word_cloud.append(result)
    print(pros_word_cloud)
    print("***************************************")
    print("*************Cons*****************")
    print(cons)
    for review in cons:
        result = filter(review)
        cons_word_cloud.append(result)
    print(cons_word_cloud)
    print("Neutral: ")
    for review in neutral:
        result = filter(review)
        neutral_word_cloud.append(result)
    print(neutral_word_cloud)
    final_pros_result = list(dict.fromkeys(pros_word_cloud))
    final_neutral_result = list(dict.fromkeys(neutral_word_cloud))
    final_cons_result = list(dict.fromkeys(cons_word_cloud))

    print("Pros: ", final_pros_result)
    print("Neutral: ", final_neutral_result)
    print("Cons: ", final_cons_result)
    n = 5
    
    biggest_pros = pd.Series(final_pros_result).value_counts()[:n].index.tolist()
    biggest_cons = pd.Series(final_cons_result).value_counts()[:n].index.tolist()
    print("biggest pro"  )
    print(biggest_pros)
    print("biggest cons" )
    print(biggest_cons)
    return {"pros":biggest_pros, "cons" :biggest_cons }