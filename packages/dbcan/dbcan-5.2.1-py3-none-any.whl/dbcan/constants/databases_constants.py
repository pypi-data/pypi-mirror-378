#############constants for downloading dbCAN databases##############################

BASE_URL = "https://bcb.unl.edu/dbCAN2/download/run_dbCAN_database_total/db_current"

# main dbCAN database
CAZY_DB_URL = f"{BASE_URL}/CAZy.dmnd"
HMMER_DB_URL = f"{BASE_URL}/dbCAN.hmm"
DBCAN_SUB_DB_URL = f"{BASE_URL}/dbCAN_sub.hmm"
DBCAN_SUB_MAP_URL = f"{BASE_URL}/fam-substrate-mapping.tsv"

# TF/ STP/ TCDB/ Peptidase/ SulfAtlas for functional annotation
TCDB_DB_URL = f"{BASE_URL}/TCDB.dmnd"
TF_DB_URL = f"{BASE_URL}/TF.hmm"
STP_DB_URL = f"{BASE_URL}/STP.hmm"
TF_DIAMOND_DB_URL = f"{BASE_URL}/TF.dmnd"
PEPTIDASE_DB_URL = f"{BASE_URL}/peptidase_db.dmnd"
SULFATLAS_DB_URL = f"{BASE_URL}/sulfatlas_db.dmnd"

# PUL
PUL_DB_URL = f"{BASE_URL}/PUL.dmnd"
PUL_MAP_URL = f"{BASE_URL}/dbCAN-PUL.xlsx"
PUL_ALL_URL = f"{BASE_URL}/dbCAN-PUL.tar.gz"

# Pfam
#PFAM_DB_URL = f"{BASE_URL}/Pfam-A.hmm"

# all database names and urls
DATABASES_CAZYME = {
            "CAZy.dmnd": CAZY_DB_URL,
            "dbCAN.hmm": HMMER_DB_URL,
            "dbCAN-sub.hmm": DBCAN_SUB_DB_URL,
            "fam-substrate-mapping.tsv": DBCAN_SUB_MAP_URL,
        }

DATABASES_CGC = {
            "TCDB.dmnd": TCDB_DB_URL,
            "TF.hmm": TF_DB_URL,
            "TF.dmnd": TF_DIAMOND_DB_URL,
            "STP.hmm": STP_DB_URL,
            "PUL.dmnd": PUL_DB_URL,
            "dbCAN-PUL.xlsx": PUL_MAP_URL,
            "dbCAN-PUL.tar.gz": PUL_ALL_URL,
            "peptidase_db.dmnd": PEPTIDASE_DB_URL,
            "sulfatlas_db.dmnd": SULFATLAS_DB_URL,
        }

COMPRESSED_DBCAN_PUL = "dbCAN-PUL.tar.gz"