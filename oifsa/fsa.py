import requests
import xmltodict
import pandas as pd
from tqdm import tqdm

from bs4 import BeautifulSoup

import sqlite3

def getDataHTML(url='http://ratings.food.gov.uk/open-data/en-GB'):
    html=requests.get(url)
    return html

def _getDataList(html):
    def span(cell):
        return cell.find('span').text
    
    soup=BeautifulSoup(html.content, "html5lib")
    #BeautifulSoup has a routine - find_all() - that will find all the HTML tags of a particular sort
    #Links are represented in HTML pages in the form <a href="http//example.com/page.html">link text</a>
    #Grab all the <a> (anchor) tags...
    souptables=soup.find("div",{'id':'openDataStatic'}).findAll('tbody')
    items=[]
    th=soup.find("div",{'id':'openDataStatic'}).find('thead').findAll('th')
    header = [span(th[i]) for i in range(len(th))]
    for table in souptables:
        for tr in table.findAll('tr'):
            td = tr.find_all("td")
            a=td[3].find('a')
            if a.text=='English language':
                items.append( (span(td[0]),span(td[1]), span(td[2]),a['href'] ) )
    df=pd.DataFrame(items)
    df.columns=header
    return df

def getDataList():
    #Get the download page HTML
    html = getDataHTML()
    #Extract the links
    df = _getDataList(html)
    return df
    
    
def checkcols(conn,df,table):
    ''' Add new cols to database table if we want to add rows with additional cols '''
    
    #Check to see if we're trying to add rows containing cols not in the db table
    dbcols = pd.read_sql('PRAGMA table_info("{}");'.format(table),conn)['name']
    newcols = list(set(df.columns) - set(dbcols))
    if newcols:
        c = conn.cursor()
        for newcol in newcols:
            q='ALTER TABLE "{}" ADD COLUMN "{}" TEXT;'.format(table,newcol)
            c.execute(q)
    
def append(conn, df, table):
    ''' Append a new set of data to the database table '''
    
    q="SELECT name FROM sqlite_master WHERE type='table' AND name='{}';".format(table)
    if len(pd.read_sql(q,conn)):
        checkcols(conn,df,table)
    df.to_sql(table, conn, index=False, if_exists='append')

def save_fsa_data(url, conn, table):
    ''' Download XML data file and add the data to the database '''
    
    r=requests.get(url)
    dd=xmltodict.parse(r.text)
    dj=pd.DataFrame(dd['FHRSEstablishment']['EstablishmentCollection']['EstablishmentDetail'])

    dj['RatingDate']=pd.to_datetime(dj['RatingDate'], errors='coerce')
    dj = pd.concat([dj.drop(['Scores'], axis=1), dj['Scores'].apply(pd.Series)], axis=1)
    dj = pd.concat([dj.drop(['Geocode'], axis=1), dj['Geocode'].apply(pd.Series)], axis=1)
    append(conn, dj, table)
    
def download_all(conn, links, table):
    for url in tqdm(links):
        save_fsa_data(url, conn, table)
    
#dbname='testdball.db'
#conn = sqlite3.connect(dbname)
#metadata_table = 'fsa_ratings_metadata'
#getDataList().to_sql(metadata_table, conn, index=False, if_exists='replace')

#table = 'ratings'
#download_all(conn, table)
