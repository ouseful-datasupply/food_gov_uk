from pandas import DataFrame, concat, json_normalize
import requests

class FoodStandardsAgencyAPI():
    BASE_URL = "https://api.ratings.food.gov.uk/Establishments"

    def __init__(
        self,
        api_token=None,
        db=None,
        initialize_tables=True,
        use_cache=True,
        cache_name="fsa_cache",
        cache_expire_after=3600,
        cache_backend="sqlite",
    ):
        self.session = None

        # Set up the session with or without caching
        if use_cache:
            import requests_cache

            self.session = requests_cache.CachedSession(
                cache_name=cache_name,
                backend=cache_backend,
                expire_after=cache_expire_after,
            )
            print(f"Caching enabled with {cache_backend} backend: {cache_name}")
        else:
            self.session = requests.Session()
            print("Caching disabled")

    def _create_df(self, jsondata):
        dj = DataFrame.from_records(jsondata)
        # have the geodata and scroes in separate tables
        # Lat-long need cast to float
        # try:
        #    dj = concat([dj.drop(['Scores'], axis=1), dj['Scores'].apply(Series)], axis=1)
        #    dj = concat([dj.drop(['Geocode'], axis=1), dj['Geocode'].apply(Series)], axis=1)
        # except:
        #    print("wtf")
        return dj

    def query_FSA_API(self, output="df", pageNumber=1, pageSize=20, all=False, **kwargs):
        """
        Query the FSA ratings API.
        
        Args:
            output (str): Output format, 'df' for DataFrame or 'json' for raw JSON
            pageNumber (int): Starting page number for pagination
            pageSize (int): Number of results per page
            all (bool): If True, retrieve all pages of results
            **kwargs: Additional query parameters to pass to the API
        
        Returns:
            DataFrame or dict: Results in the requested format
        """
        # Start with the kwargs dictionary
        params = kwargs.copy()

        # Add pagination parameters
        params['pageNumber'] = pageNumber
        params['pageSize'] = pageSize

        # Set the headers
        headers = {
            "Accept": "application/json",
            "x-api-version": "2",  # Specify the API version if needed
        }

        # Initial API call to get first page
        response = self.session.get(self.BASE_URL, headers=headers, params=params)

        if response is None:
            return None

        # If all=False, just return the single page results
        if not all:
            if output == "df":
                return self._create_df(response.json()['establishments'])
            else:
                return response.json()

        # If all=True, we need to fetch all pages
        all_results = response.json()['establishments']  # Adjust based on your API response structure

        total_pages = response.json()['meta']['totalPages']  # Adjust based on your API structure

        # Fetch remaining pages (only if all=True)
        for page in range(pageNumber + 1, total_pages + 1):
            params['pageNumber'] = page
            page_response = self.session.get(self.BASE_URL, headers=headers, params=params)

            if page_response is None:
                break

            page_results = page_response.json()['establishments']
            all_results.extend(page_results)

            # Optional: Add a progress indicator
            # print(f"Retrieved page {page} of {total_pages}")

        # For all=True, return combined results
        if output == "df":
            data = self._create_df(all_results)
            data = concat([data, json_normalize(data["geocode"]).add_prefix("geo_")], axis=1)
            data = concat([data, json_normalize(data["scores"]).add_prefix("score_")], axis=1)
            return data

        # Return JSON as default
        return all_results

query_FSA_API = FoodStandardsAgencyAPI().query_FSA_API
