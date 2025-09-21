from lsyflasksdkcore.export.csv import CvsResponse
from lsyflasksdkcore.export.xls import XlsResponse

cvs = CvsResponse()
xls = XlsResponse()


def init_excel(app):
    cvs.init_app(app)
    xls.init_app(app)
