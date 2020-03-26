import click
import oifsa.fsa as fsa
import sqlite3
from tqdm import tqdm, tqdm_pandas

def droptable(conn,table):
    cursor = conn.cursor()
    cursor.execute('''DROP TABLE IF EXISTS {}'''.format(table))
    conn.commit()


@click.command()
@click.option('--dbname', default='fsa_ratings_all.db',  help='SQLite database name (default: fsa_ratings_all.db)')
@click.option('--ratingstable', default='ratingstable', help='FSA Ratings table name (default: ratingstable)')
@click.argument('command')
def cli(dbname, ratingstable, command):
    conn = sqlite3.connect(dbname)
    click.echo('Using SQLite3 database: {}'.format(dbname))
    if command == 'collect':
        metadata_table = 'fsa_ratings_metadata'
        #Drop table for now
        droptable(conn,metadata_table)
        print('Scraping table links...')
        df= fsa.getDataList()
        df.to_sql(metadata_table, conn, index=False, if_exists='replace')
        #Register pandas with tqdm
        tqdm.pandas(tqdm())
        #Drop table for now
        droptable(conn,ratingstable)
        df['Link'].progress_apply(fsa.save_fsa_data,conn=conn, table=ratingstable)
