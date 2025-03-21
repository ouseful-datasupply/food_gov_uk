import click
import ouseful_fsa_datasupply.fsa as fsa
import sqlite3
from tqdm import tqdm, tqdm_pandas

def droptable(conn,table):
    cursor = conn.cursor()
    cursor.execute('''DROP TABLE IF EXISTS {}'''.format(table))
    conn.commit()


@click.command()
@click.option('--dbname', default='fsa_ratings_all.db',  help='SQLite database name (default: fsa_ratings_all.db)')
@click.option('--ratingstable', default='ratingstable', help='FSA Ratings table name (default: ratingstable)')
@click.option('--area', default=None, help='Grab data for area')
@click.option('--authority', default=None, help='Grab data for Local Authority')
@click.option('--drop/--no-drop', default=False, help='Drop ratings table')
@click.argument('command')
def cli(dbname, ratingstable, area, authority,drop, command):
    conn = sqlite3.connect(dbname)
    click.echo('Using SQLite3 database: {}'.format(dbname))
    if command == 'collect':
        metadata_table = 'fsa_ratings_metadata'
        #Drop table for now
        droptable(conn,metadata_table)
        print('Scraping table links...')
        if area:
            print(f'Grabbing data for {area}')
        elif authority:
            print(f'Grabbing data for {authority}')
        df = fsa.getDataList(area=area, authority=authority)
        df.to_sql(metadata_table, conn, index=False, if_exists='replace')
        #Register pandas with tqdm
        tqdm.pandas()
        if drop:
            #Drop table for now
            droptable(conn,ratingstable)
        df['Link'].progress_apply(fsa.save_fsa_data, conn=conn, table=ratingstable)
