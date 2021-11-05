import os, json

from typing import Generator, Optional

class CompanyList():
    
    FOLDER_PATH = './company_info'

    @classmethod
    def get_company_list(cls, file_name: Optional[str]=None) -> Generator:
        if not file_name:
            file_name = 'tw_fifty.json'

        file_path = os.path.join(cls.FOLDER_PATH, file_name)
        with open(file_path, 'r') as rf:
            all_company_data = json.load(rf)

        for company_data in all_company_data:
            yield {
                'company_id': company_data['company_id'],
                'company_name': company_data['company_name'],
            }
