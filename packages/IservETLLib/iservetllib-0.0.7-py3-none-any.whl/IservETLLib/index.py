import pandas as pd
from DatabaseManager import DBManager
from LogManager import Logger, LogLevel, FluentConf
from Helpers import Helpers


CONNECTION_STRING = ""
ETL = "import_calendar.ipynb"
UID = "ad03135a-236a-4fde-97d1-1f5c10907b96"
OUTPUT_DIR = "./files/output"
USR_ID = "967"

__CONNECTION_STRING=CONNECTION_STRING if 'CONNECTION_STRING' in locals() else None
__OUTPUT_DIR=OUTPUT_DIR if 'OUTPUT_DIR' in locals() else ''
__ETL=ETL if 'ETL' in locals() else 'unknown etl'
# # __FILEPATHNAME=FILEPATHNAME if 'FILEPATHNAME' in locals() else ''
# __FILEPATHNAME=os.path.join(OUTPUT_DIR.rsplit('/output', 1)[0], FILEPATHNAME) if 'FILEPATHNAME' in locals() else None #Используются на проде
__LOG_FILE = __OUTPUT_DIR + '/output.log'
__USR_ID=USR_ID if 'USR_ID' in locals() else 'null'


if __name__ == "__main__":

    logger = Logger(__ETL,  __USR_ID, __LOG_FILE)
    db_manager = DBManager(__ETL, __CONNECTION_STRING, logger)
    # logger.init_fluent(LogLevel.INFO, FluentConf('10.199.236.8', 24224))
    logger.log("asdas")
    print(Helpers.generate_route_number('asdad'))

    print(pd.DataFrame(db_manager.of_users(__USR_ID)))