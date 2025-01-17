
import pandas as pd
from sqlalchemy import create_engine
import dotenv
from os import getenv
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from json import loads
from pandas.io.json import json_normalize
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import KNeighborsTransformer

import pickle


class Transformer():
    def __init__(self):
        # try to load data from .env

        self.load_data()

        self.tokenizer = Tokenizer(num_words=1000, lower=True)
        return
    
    def load_data(self):
        """A function that takes the DATABASE_URL and fetches the contents of the
        strain_info table then saves it to a df for training the model.
        """
        dotenv.load_dotenv()
        alt = 'DATABASE_URL'
        db_url = getenv("DATASOURCE", default=alt)

        engine = create_engine(db_url)
        df = pd.read_sql("SELECT * FROM strain_info", engine)
        self.df = df
        return df

    def transform(self, document: pd.DataFrame, negative: list, ignore: list) -> pd.DataFrame:
        """A function transforms the features from the input dataframe into a Document-term matrix then takes those 
        Arguments:
        -------------
        document {list} : An array like list of strings representing a document to be transformed
        negitive {list} : the list of negitive features to use in calculating the dtm products
        ignore {list} : a list of features to ignore in the dtm product
        Returns:
        -------------
        combined_scaled {pd.DataFrame} : A dataframe of the transformed document's tfidf
        """

        dtm = [0] * 1000

        for i in document.columns:
            if i in ignore:
                pass
            else:
                # takes the document term frequency and if it is
                # a neg feature then we want to subtract  it from the combined dtm
                if i in negative:
                    dtm -= self.find_dtm(document[i])
                # otherwise i want to add it to the combined dtm
                else:
                    dtm += self.find_dtm(document[i])

        mm = MinMaxScaler()
        combined_scaled_values = mm.fit_transform(dtm)
        combined_scaled_columns = dtm.columns.tolist()
        combined_scaled = pd.DataFrame(combined_scaled_values,
                                       columns=combined_scaled_columns)
        combined_scaled.fillna(0, inplace=True)
        return combined_scaled, document.index.tolist()

    def find_dtm(self, feature):
        """A function to take a feature and tokenize then return a tfidf df of that input
        """
        self.tokenizer.fit_on_texts(feature)
        a = self.tokenizer.texts_to_matrix(feature, mode='tfidf')
        config = self.tokenizer.get_config()
        feature_names = json_normalize(loads(
            config['word_index'])).columns.tolist()
        dtm = pd.DataFrame(a)
        return dtm


if __name__ == "__main__":
    tr = Transformer()
    negative = ['negative']
    ignore = []
    user_transformed, y = tr.transform(
        pd.DataFrame({'name': "blue berry kush",
                      'race': 'sativa',
                      'flavors': ['blueberry', 'sweet'],
                      'negative': ['dry mouth', 'dry eyes'],
                      'positive': ['creativity', 'stress'],
                      'medical': ['ptsd', 'stress'],
                      'description': "blueberry kush my dude blueberry_kush:10, whitewhidow:10 ",
                      }), negative, ignore)
    model = KNeighborsTransformer()
    model.fit()

