import requests
import xmltodict
import pandas as pd
from tqdm import tqdm
from time import sleep
from bs4 import BeautifulSoup

import sqlite3

XML_BASE = "https://ratings.food.gov.uk"


def getDataHTML(url="https://ratings.food.gov.uk/open-data"):
    html = requests.get(url)
    return html


def _getDataList(html, area="", authority=""):
    # def span(cell):
    #    return cell.find('span').text
    df = pd.DataFrame()
    soup = BeautifulSoup(html.content, "html5lib")
    # BeautifulSoup has a routine - find_all() - that will find all the HTML tags of a particular sort
    # Links are represented in HTML pages in the form <a href="http//example.com/page.html">link text</a>
    # Grab all the <a> (anchor) tags...
    souptables = soup.findAll("table", {"class": "fhrs-open-data"})

    for table in souptables:
        caption = table.find("caption")
        caption_text = caption.text.strip() if caption else ""
        if area and area.lower() != caption_text.lower():
            continue

        items = []
        th = table.find("thead").findAll("th")
        header = [th[i].text for i in range(len(th))]
        for tr in table.findAll("tr"):
            td = tr.find_all("td")
            if not len(td):
                continue
            elif (
                authority
                and authority != td[0].text.replace("(English language)", "").strip()
            ):
                continue
            a = td[0].find("a")
            if "(English language)" in a.text:
                items.append(
                    (
                        td[0].text.replace("(English language)", "").strip(),
                        td[1].text.strip(),
                        td[2].text.strip(),
                        a["href"],
                        caption_text,
                    )
                )
        df = pd.concat([df, pd.DataFrame(items)])
    # TO DO - check head==df.columns ?
    if df.empty:
        return pd.DataFrame(
            columns=[
                "Local authority",
                "Last update",
                "Number of businesses",
                "Link",
                "Area",
            ]
        )
    else:
        df.columns = header + ["Link", "Area"]
    return df


def getDataList(area="", authority=""):
    # Get the download page HTML
    html = getDataHTML()
    # Extract the links
    df = _getDataList(html, area=area, authority=authority)
    return df


# +
# getDataList()
# -


def checkcols(conn, df, table):
    """Add new cols to database table if we want to add rows with additional cols"""

    # Check to see if we're trying to add rows containing cols not in the db table
    dbcols = pd.read_sql('PRAGMA table_info("{}");'.format(table), conn)["name"]
    newcols = list(set(df.columns) - set(dbcols))
    if newcols:
        c = conn.cursor()
        for newcol in newcols:
            q = 'ALTER TABLE "{}" ADD COLUMN "{}" TEXT;'.format(table, newcol)
            c.execute(q)


def append(conn, df, table):
    """Append a new set of data to the database table"""

    q = "SELECT name FROM sqlite_master WHERE type='table' AND name='{}';".format(table)
    if len(pd.read_sql(q, conn)):
        checkcols(conn, df, table)
    df.to_sql(table, conn, index=False, if_exists="append")


def download_and_parse_fsa_data(url, delay=1):
    """
    Download XML data file from FSA and parse it into a pandas DataFrame

    Args:
        url (str): URL of the XML data file
        delay (int): Delay in seconds before making the request

    Returns:
        pandas.DataFrame: Parsed data or None if parsing failed
    """
    # Play a bit nicer
    sleep(delay)

    # Download the XML file
    if url.startswith("/"):
        url = f"{XML_BASE}{url}"
    #print(f"Getting: {url}")
    r = requests.get(url)

    # Try to parse the XML file
    try:
        dd = xmltodict.parse(r.text)
    except Exception as e:
        print(f"Failed to parse file at {url}: {e}")
        return None

    # Try to convert to DataFrame
    try:
        dj = pd.DataFrame(
            dd["FHRSEstablishment"]["EstablishmentCollection"]["EstablishmentDetail"]
        )
    except Exception as e:
        print(f"Failed to convert to DataFrame for {url}: {e}")
        return None

    # Process the data
    try:
        # Convert rating date to datetime
        dj["RatingDate"] = pd.to_datetime(dj["RatingDate"], errors="coerce")

        # Expand nested dictionaries
        if "Scores" in dj.columns:
            dj = pd.concat(
                [dj.drop(["Scores"], axis=1), dj["Scores"].apply(pd.Series)], axis=1
            )

        if "Geocode" in dj.columns:
            dj = pd.concat(
                [dj.drop(["Geocode"], axis=1), dj["Geocode"].apply(pd.Series)], axis=1
            )

        return dj
    except Exception as e:
        print(f"Error processing data from {url}: {e}")
        return pd.DataFrame()


def save_fsa_data(url, conn, table, delay=1):
    """Download XML data file and add the data to the database"""
    dj = download_and_parse_fsa_data(url, delay=delay)
    if not dj.empty:
        try:
            append(conn, dj, table)
        except:
            pass


def download_all(conn, links, table):
    for url in tqdm(links):
        save_fsa_data(url, conn, table)


# dbname='testdball.db'
# conn = sqlite3.connect(dbname)
# metadata_table = 'fsa_ratings_metadata'
# getDataList().to_sql(metadata_table, conn, index=False, if_exists='replace')

# table = 'ratings'
# download_all(conn, table)
