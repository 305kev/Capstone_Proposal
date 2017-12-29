from imp import reload

import requests
from bs4 import BeautifulSoup
import pandas as pd
from sys import argv
from collections import defaultdict
from time import sleep
import os
import boto3
from io import StringIO, BytesIO

try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin
import sys

reload(sys)
sys.setdefaultencoding('utf8')


def run_scraper(current_url, dft):
    """
    Run the web scraper that will scrape Findlaw
    :param current_url: string, the initial URL to scrape
    :param dft: Pandas dataframe, the listings data from previous scrapings
    :return: dft: Pandas dataframe containing scraped information
    """

    soup = create_soup(current_url)
    cases = defaultdict(list)

    # Run the scraper until it runs out of pages to scrape
    flag = u'\xbb'
    last_page = False

    while u'\xbb' in flag or last_page == False:
        # 1.) Get each court case listing

        for row in soup.find_all(name="tr", attrs={"class": "srpcaselawtr"}):
            cases = add_case_info(row, cases)
            sleep(2)

        # 2.) Get next page's pagination info + set new flag
        try:
            current_url = get_next_url(current_url, soup)
            soup = create_soup(current_url)
            next_list = []
            for i in soup.find_all(name="a", attrs={"class": "pgnum"}):
                next_list.append(i.text)
        except:
            break

        flag = next_list[-1]
        if u'\xbb' not in flag and last_page == False:
            flag = u'\xbb'
            last_page = True

    dft = dft.append(pd.DataFrame(cases), ignore_index=True)
    return dft


def create_soup(url):
    """
    Get the HTML contents of the URL.
    :param url: string, the url to scrape
    :return: soup: a BeautifulSoup object
    """
    page = requests.get(url)
    return BeautifulSoup(page.text, "html.parser")


def get_next_url(current_url, soup):
    """
    Get the URL of the next listings page.
    :param soup: Beautiful soup object
    :return: string, the URL of the next webpage
    """

    d = [i.get('href') for i in soup.find_all(name="a", attrs={"class": "pgnum"})][-1]
    return urljoin(current_url, d)


def add_case_info(row, case_dict):
    """
    Get the results of scraping a single case.
    :param row: the contents of a single court case's row tag
    :param case_dict: the currently scraped court cases
    :return: case_dict, the desired scraping information

    """
    case_dict["date"] += [get_date(row)]
    case_dict["court"] += [get_court(row)]
    case_dict["case_title"] += [get_case_title(row)]
    case_dict["docket"] += [get_docket(row)]
    case_dict["tags"] += [get_tags(row)]
    case_dict["type_of_law"] += ["case"]
    case_dict["web_source"] += ["findlaw.com"]

    case_link = get_case_url(row)

    case_dict["url"] += [case_link]
    case_dict["case_text"] += [get_case_text(case_link)]

    return case_dict


def get_case_title(row):
    """
    extract the title from the row tag
    :row: tag object, the row tag from a case
    :return: string, the case title
    """
    title = row.find('a').get("title")
    return title


def get_court(row):
    """
    extract the court name from the row tag
    :row: tag object, the row tag from a case
    :return: string, the court
    """
    court = row.find('span').text
    return court


def get_tags(row):
    """
    extract the types of law involved as law tags from the row tag
    :row: tag object, the row tag from a case
    :return: string, the law tags
    """
    tags = row.find('i').text
    return tags


def get_date(row):
    """
    extract decision date from the row tag
    :row: tag object, the row tag from a case
    :return: string, decision date
    """
    decision_date = row.find_all('td', {'valign': 'top'})[-2].text
    return decision_date


def get_docket(row):
    """
    extract docket number from the row tag
    :row: tag object, the row tag from a case
    :return: string, docket number
    """
    docket_number = row.find_all('td', {'valign': 'top'})[-1].text
    return docket_number


def get_case_url(row):
    """
    extract case URL from the row tag
    :row: tag object, the row tag from a case
    :return: string, the URL of case text
    """
    initial_url = row.find('a').get('href')
    new_soup = create_soup(initial_url)
    check_url = new_soup.find(name="div", attrs={"class": "btn_read"}).find('a').get('href')
    check_soup = create_soup(check_url)

    if check_soup.find_all("a", {"target": "new"}):
        case_url = second_check(check_url)
    else:
        case_url = check_url
    return case_url


def second_check(url):
    soup = create_soup(url)
    for i in soup.find_all("p"):
        try:
            href = i.a.get('href')
            return href
            break

        except:
            continue


def get_case_text(link):
    """
    Get the raw text of the case from the linked webpage.
    :param link: str, the url of case text webpage
    :return: if case text as html: str, the case text from the webpage
            else: nothing.
    """
    text_soup = create_soup(link)

    # remove all javascript and stylesheet code
    for script in text_soup(["script", "style"]):
        script.extract()

    text = text_soup.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())

    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))

    # drop any blank lines and get only relevant text
    case = []

    for chunk in chunks:
        if chunk and 'United States Supreme Court' in chunk:
            case.append(chunk)
            for chunk in chunks:
                if 'FindLaw Career Center' in chunk:
                    break
                else:
                    case.append(chunk)
    return '\n'.join(case)


def create_df_new():
    """
    If it doesn't exist, create the initial case_data file
    :return: New Dataframe
    """
    df_new = pd.DataFrame(columns=["date", "court", "case_title",
                                   "docket", "tags", "type_of_law",
                                   "web_source", "url", "case_text"])
    return df_new


def write_file_to_s3(df_write):
    """
    Save the updated dataframe to a file on the project's AWS S3 bucket.
    :param df_write: DataFrame to write to file
    :return: None
    """
    for column in df:
        df_write[column] = df_write[column].str.encode('utf-8')

    try:
        csv_buffer = StringIO()
        df_write.to_csv(csv_buffer, index=False)

    except:
        csv_buffer = BytesIO()
        df_write.to_csv(csv_buffer, index=False)

    s3 = boto3.resource("s3", aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
                        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"])
    s3.Object("court-case-data", "us_supreme_court.csv").put(Body=csv_buffer.getvalue())


def access_s3_to_df():
    """
    Access the project's S3 bucket and load the file into a dataframe for appending.
    :return: df: a pandas dataframe containing the data.
    """

    s3 = boto3.client("s3", aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
                      aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"])
    try:
        obj = s3.get_object(Bucket="court-case-data", Key="us_supreme_court.csv")
        return pd.read_csv(BytesIO(obj["Body"].read()))
    except:
        return create_df_new()


if __name__ == "__main__":
    """
    Code that runs if called from the command line
    Call: python findlaw_scraper.py 

    """
    print('U.S. Supreme Court')
    df = access_s3_to_df()
    first_url = 'http://caselaw.findlaw.com/summary/search/?query=filters&court=us-supreme-court&dateFormat=yyyyMMdd&topic=cs_42&pgnum=1'
    df = run_scraper(first_url, df)
    write_file_to_s3(df)
    print(df.tail())
