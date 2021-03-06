# food\_gov\_uk
Tools for grabbing data from food.gov.uk

`pip install --upgrade git+https://github.com/ouseful-datasupply/food_gov_uk.git`


[![Binder](https://mybinder.org/badge.svg)](https://mybinder.org/v2/gh/ouseful-datasupply/food_gov_uk/master)

## Command Line Interface

The CLI will scrape the [UK Food Standards Agency ratings data](https://ratings.food.gov.uk/open-data/en-GB) XML files and construct a simple SQLite database from them containing two tables:

- `fsa_ratings_metadata`: containing the name and publication date of each scraped file
- `USER-DEFINED` (default: `ratingstable`) containing the ratings data from the XML files.

The created database can then be used with tools such as [`datasette`](https://github.com/simonw/datasette/tree/master/datasette).

```
Usage: oi_fsa [OPTIONS] COMMAND

Commands:
  collect              Collect data from FSA website

Options:
  --dbname TEXT        SQLite database name (default: fsa_ratings_all.db)
  --ratingstable TEXT  FSA Ratings table name (default: ratingstable)
  --area TEXT          Specfiy an area to download data for
  --authority TEXT     Specfiy a local authority to download data for
  --help               Show this message and exit.
```
