from math import ceil
import re

class MyPaginator():
    def __init__(self, num_of_objects, request, max_per_page):
        self.request = request
        self.num_of_objects = num_of_objects
        self.page = self.validate_page(self.request.get('page'))
        self.max_per_page = max_per_page

        get_page = self.get_page()
        self.results_bottom = get_page[0]
        self.results_top = get_page[1]

    def request_filters(self):
        request = self.request.dict()
        qs_filters = ""
        for field in request:
            qs_filters += "&{field}={field_value}".format(field=str(field), field_value=str(request[field]))

        return re.sub('&page=[\d]+', '', qs_filters).replace(',', "%2C")
    
    def validate_page(self, page):
        try:
            page = int(page)
        except (TypeError, ValueError):
            page = 1
        
        if page < 1: 
            page = 1
        
        return page

    def get_page(self):
        page = self.page
        bottom = (page - 1) * self.max_per_page
        top = bottom + self.max_per_page

        if top > self.num_of_objects: 
            top = self.num_of_objects

        return bottom, top

    def has_next(self):
        return self.results_top < self.num_of_objects

    def has_previous(self):
        return self.results_top > self.max_per_page

    def next_page_number(self):
        return self.validate_page(self.page + 1)

    def previous_page_number(self):
        return self.validate_page(self.page - 1)

    def last_page_number(self):
        return int(ceil(self.num_of_objects / self.max_per_page))