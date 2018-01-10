
"""
Script that updates the court case csv file
with the added HTML Format and loads it into AWS S3 Bucket

"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
from sys import argv
from collections import defaultdict
from time import sleep
import os
import boto3
from io import StringIO, BytesIO
import re
from time import sleep
try:
    from urlparse import urljoin
except:
    from urllib.parse import urljoin
import unicodedata
import pandas as pd



def find_format(url):
#     soup = create_soup(url)
    try:
        content = requests.get(url).content
        soup = BeautifulSoup(content, "html.parser")
        html_format = soup.findAll('div', {'class': 'caselawcontent searchable-content'})
    except:
        html_format = None
    return html_format


def access_s3_to_df():
    """
    Access the project's S3 bucket and load the file into a dataframe for appending.
    :return: df: a pandas dataframe containing the data.
    """

    s3 = boto3.client("s3", aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
                      aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"])
    try:
        obj = s3.get_object(Bucket="court-case-data", Key="merged_data_with_html_format.csv")
        return pd.read_csv(BytesIO(obj["Body"].read()))
    except:
        return None

def write_file_to_s3(df_write):
    """
    Save the updated dataframe to a file on the project's AWS S3 bucket.
    :param df_write: DataFrame to write to file
    :return: None
    """
    try:
        csv_buffer = StringIO()
        df_write.to_csv(csv_buffer, index=False)
    except:
        csv_buffer = BytesIO()
        df_write.to_csv(csv_buffer, index=False)

    s3 = boto3.resource("s3", aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
                        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"])
    s3.Object("court-case-data", "merged_data_with_html_format.csv").put(Body=csv_buffer.getvalue())

if __name__ == "__main__":
    """
    Code that runs if called from the command line
    Call: python add_html_format.py

    """
    df = access_s3_to_df()
    df["html_format"] = df['url'].apply(lambda x: find_format(x))
    write_file_to_s3(df)
    print(df.tail())
