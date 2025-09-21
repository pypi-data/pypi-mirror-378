from lsyflasksdkcore.export.csv import CsvResponse
from lsyflasksdkcore.export.xls import XlsResponse

csv = CsvResponse()
xls = XlsResponse()


def init_excel(app):
    csv.init_app(app)
    xls.init_app(app)
