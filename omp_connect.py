

def get_omp_connection(pw=''):
    """Returns ODBC connection to OTP database"""

    svrName='RQFH5SRVIPLANFL'   #Server, port, DB all come from DSN, so this is a bit misleading
    dbName='OTP_Database'
    usrName='DBLOOK'
    drvr='MIMER'
    portNum='1360'

    cnxn = getODBCconnection(svrName, dbName, usrName, drvr, portNum, pw)

    return cnxn