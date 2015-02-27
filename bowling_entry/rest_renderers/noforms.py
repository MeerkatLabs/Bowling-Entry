from rest_framework.renderers import BrowsableAPIRenderer


class NoFormBrowsableAPIRenderer(BrowsableAPIRenderer):

    def get_raw_data_form(self, data, view, method, request):
        return None