import functions_framework
from transformers import pipeline
import pandas as pd
import nltk

nltk.download(["stopwords"])
from nltk.stem.porter import PorterStemmer
# library to clean data
import re
from nltk.corpus import stopwords
from nltk.corpus import state_union
from nltk.tokenize import PunktSentenceTokenizer


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
    sent_pipeline = pipeline("sentiment-analysis")
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
        analysis = sent_pipeline(text)

        if analysis[0]['label'] == "POSITIVE":
            if analysis[0]['score'] > .90:
                pros.append(text)
            else:
                neutral.append(text)
        elif analysis[0]['label'] == "NEGATIVE":
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