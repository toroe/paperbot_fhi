import os
import random
import requests
import glob
import pandas as pd
from graphdriver import GraphDBDriver
"""
DATABASE INITILIAZE SCRIPT
Initiliazes graph data for provided file structure.
GEN1 Filestructure: Single XLS Web of Science Advanced Search Output
GEN2 + LINKED CITATIONS Filestructure: XLS Web of Science Advanced Search Output names as DOI it refers to 
"""

"""
Loads and parses WOS Advanced Search Output
Parses to Pandas Dataframe
Returns Dataframe
"""
def load_xls(filename):
    data = pd.read_excel(filename)
    data["Publication Year"] = data["Publication Year"].fillna(0).astype(int)
    data.dropna(subset=["DOI"], inplace=True)
    df = pd.DataFrame(data, columns=["Author Full Names", "Source Title", "Article Title", 
                                    "Abstract","Document Type", "Keywords Plus", 
                                    "DOI","Book DOI", "Publication Year"])
    return df
"""
PARSE DF into structure for further processing
ARTICLE STRUCTURE:
title: str
abstract: str
authors: list(str)
doi: str
journal: str
keyword: list(str)
publication_year: int
generation: int

Input:
DATAFRAME: pandas dataframe
ARTICLE GENERATION: integer
"""
def prepare_articles(df, generation):
    df['Abstract'] = df['Abstract'].fillna("")
    articles = []
    for index, row in df.iterrows():
        article = {}
        article["title"] = row[2]
        if row[3] is not None:
            article["abstract"] = row[3]
        else:
            article["abstract"] = ""
        try:
            article["authors"] = prepare_names(row[0].split(";"))
        except AttributeError as e:
            article["authors"] = []
        article["doi"] = row[6]
        article["journal"] = row[1] 
        try:
            article["keywords"] = prepare_keywords(row[5].split(";"))
        except AttributeError as e:
            article["keywords"] = []
        try:
            article["publication_year"] = row[8]
        except IndexError as e:
            print(row)
        article["generation"] = generation
        articles.append(article)
    return articles

def prepare_names(name_list):
    cleaned_names = []
    for key, name in enumerate(name_list):
        
        new = name.split(",")
        try:
            full_names = new[1]+ " " +new[0]
        except IndexError as e:
            full_names = new[0]
        full_names = full_names.strip().replace("  ", " ")
        cleaned_names.append(full_names)
    return cleaned_names

def prepare_keywords(keywords):
    keywords_ = []
    for keyword in keywords:
        keywords_.append(keyword.lower().strip())
    return keywords_
"""
DOI ENCODING AND DECODING FOR FILE RENAMING PURPOSES
"""
def encode_doi(doi):
    doi = doi.replace("/", "%42%")
    encoded_doi = doi.replace(".", "%24%")
    return encoded_doi
def decode_doi(encoded_doi):
    doi = encoded_doi.replace("%42%", "/")
    doi = doi.replace("%24%", ".")
    return doi
"""
Creates the first generation of articles in database. Input genone.xls
"""
def create_base_generation(base_gen_filepath: str, db_driver: GraphDBDriver):
    dataframe = load_xls(base_gen_filepath)
    articles = prepare_articles(dataframe, 1)
    for article in articles:
        db_driver.add_article(article)
"""
Creates and links 2 and 0 generation of articles. 
Input file path:
data/GEN2/
data/GEN1_REFERENCEE/

GEN2 forard_cited=False, generation= 2
GEN1_REFERENCEE forard_cited=True, generation= 0
"""
def create_linked_generation(linked_gen_filepath: str, db_driver: GraphDBDriver):
    for encoded_doi_file in glob.glob(linked_gen_filepath+"*"):
        data = pd.read_excel(encoded_doi_file)
        data["Publication Year"] = data["Publication Year"].fillna(0).astype(int)
        data.dropna(subset=["DOI"], inplace=True)
        df = pd.DataFrame(data, columns=["Author Full Names", "Source Title", "Article Title", "Abstract","Document Type", "Keywords Plus", "DOI","Book DOI", "Publication Year"])
        encoded_doi = encoded_doi_file.replace(linked_gen_filepath, "").replace(".xls", "")
        doi = decode_doi(encoded_doi)
        #Genertation 0 
        articles = prepare_articles(df, generation=2)
        for article in articles:
            db_driver.add_article(article)
            db_driver.link_citing_articles(article["doi"], doi, forward_cited=False)
            print(doi)
if __name__ == "__main__":
    db_driver = GraphDBDriver("bolt://localhost:7687", os.environ["NEO4J_USER"],"$cheisse4ldder")

    create_base_generation("/home/tom/Desktop/paperbot_fhi/data/genone.xls", db_driver)