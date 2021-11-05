from datetime import datetime

class QueryParamter():

    MINIMUM_YEAR = 2000
    LACK_YEARS = {2013, 2014}
    
    def __init__(self,
            company_id: str,
            year: int,
        ):
        self.company_id = company_id
        self.year = year
        self.season = 4
        self.step = 'show'
        self.typek = 'all'

        assert self._is_valid_year(self.year),\
            ValueError(
                'Invalid year: The input year must be in {}'.format(self.__valid_years)
            )
        assert self.season == 4,\
            NotImplementedError(
                "The season only can choose 4 for now."
            )

    def _is_valid_year(self, year):
        valid_years = set(range(self.MINIMUM_YEAR, datetime.now().year))
        self.__valid_years = valid_years.difference(self.LACK_YEARS)
        return year in self.__valid_years

    @property
    def query_params(self) -> dict:
        if not self.company_id or len(self.company_id) != 4:
            raise ValueError(
                "co_id can't be empty string and "
                "its lenght must be equal to 4."
            )
        query_params = {
            'co_id': self.company_id,
            'year': self.year,
            'season': self.season,
            'step': self.step,
            'TYPEK': self.typek,
        }
        return query_params

    def concate_params(self, between_str: str='&') -> str:
        trans_params = ['{}={}'.format(k, v)\
            for k, v in self.query_params.items()
        ]
        concate_params = between_str.join(trans_params)
        return concate_params

    def __repr__(self) -> str:
        return "< query_params: {} >".format(self.query_params)


class MopsRequestInfo():

    URL_PREFIX = 'https://emops.twse.com.tw/server-java/'
    
    SEPARATE_YEAR = 2012
    REQUEST_INFO = {
        # 'share_ownership': {
        #     'method': 'GET',
        #     'url_suffix': 't164sb02_e',
        #     'query_parameters': QueryParamter,
        # },
        'balance_sheet': {
            'method': 'GET',
            'url_suffix': {
                'before': 't05st31_e',
                'after': 't164sb03_e',
            },
            'query_parameters': QueryParamter,
        },
        'income_statement': {
            'method': 'GET',
            'url_suffix': {
                'before': 't05st32_e',
                'after': 't164sb04_e',
            },
            'query_parameters': QueryParamter,
        },
        'cash_flow': {
            'method': 'GET',
            'url_suffix': {
                'before': 't05st38_e',
                'after': 't164sb05_e',
            },
            'query_parameters': QueryParamter
        } 
    }

    def __init__(self, 
            report_name: str,
            company_id: str,
            year: int
        ):
        self.report_name = report_name
        self.company_id = company_id
        self.year = year
        self.season = 4
        if self.year > self.SEPARATE_YEAR:
            self.before_or_after = "after"
        else:
            self.before_or_after = "before"

    @property
    def request_info(self) -> dict:
        request_info = self.REQUEST_INFO[self.report_name]
        request_method = request_info['method']
        # Get QueryParameter object
        ParameterObj = request_info['query_parameters']
        params = ParameterObj(self.company_id, self.year)
        url = self.URL_PREFIX + request_info['url_suffix'][self.before_or_after]
        return_info = {
            'method': request_method,
            'query_parameters': params.query_params,
        }
        if request_method == 'GET':
            # If the reuquest method is GET, it will concate the url and parameters.s
            concate_params = params.concate_params()
            url = url + '?' + concate_params
        return_info['request_url'] = url
        return return_info

    def __str__(self) -> str:
        return "< {}:{} >".format(
            self.__class__.__name__,
            self.request_info
        )
