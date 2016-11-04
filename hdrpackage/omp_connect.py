
import pyodbc
import sys


def connect_to_db():
    """Returns connection to OTP database on OTP server"""
    conn_string = "Driver={MIMER};Server=otp-server;Database=OTP_DATABASE;Uid=DBLOOK;Pwd=dblook"
    return pyodbc.connect(conn_string)


def test_db_connection():
    """Returns connection to OTP database on OTP client 8"""
    conn_string = "Driver={MIMER};Server=otp-client8;Database=OTP_DATABASE;Uid=DBLOOK;Pwd=dblook"
    return pyodbc.connect(conn_string)


def get_patient_cases(patient):
    """Returns list of cases for patient with specified ID"""
    # ----- Get database connection
    db = connect_to_db()
    try:
        c1 = db.cursor()
        try:
            c1.execute(
                """SELECT tc.SLABEL """
                """FROM BOM.PATIENT pt """
                """    INNER JOIN BOM.TCASE tc ON pt.SUID = tc.SPATIENTUID """
                """WHERE """
                """    pt.SID = '%s' """ %
                patient)
            res = c1.fetchall()
            cases = []
            for re in res:
                cases.append(re[0])
        finally:
            c1.close()
    finally:
        db.close()
    return cases


def get_plans_from_case(patient, case):
    """Returns list of plans for patient specified ID, case"""
    db = connect_to_db()
    try:
        c1 = db.cursor()
        try:
            query_str = \
                """SELECT rtplan.SLABEL """ \
                """FROM BOM.PATIENT pt """ \
                """    INNER JOIN BOM.TCASE tc ON pt.SUID = tc.SPATIENTUID """ \
                """ INNER JOIN BOM.RTPLAN rtplan ON rtplan.SCASEUID = tc.SUID """ \
                """ WHERE """ \
                """    pt.SID = '%s' AND """ \
                """    tc.SLABEL = '%s' """ % (patient, case)
            c1.execute(query_str)
            res = c1.fetchall()
            plans = []
            for re in res:
                plans.append(re[0])
        finally:
            c1.close()
    finally:
        db.close()
    return plans


def get_rtplan(
        patient,
        case,
        plan_string="",
        images=False,
        published=False):
    """Returns RT plan data for patient with specified ID, case, plan name"""
    db = connect_to_db()
    try:
        c1 = db.cursor()
        try:
            if not images:
                imagestr = " AND LOWER(rtplan.SLABEL) NOT LIKE '%image%' "
            else:
                imagestr = ""
            if published:
                pubstring = " AND rtplan.BHASDOSEMATRIX = 'T' AND rtplan.BPUBLISHED = 'T' "
            else:
                pubstring = ""
            if plan_string != "":
                plan_string = " AND (rtplan.SLABEL = '%s') " % plan_string
            querystr = """SELECT rtplan.SLABEL, rtplan.LBPART10BLOB """ \
                       """FROM BOM.PATIENT pt """ \
                       """    INNER JOIN BOM.TCASE tc ON pt.SUID = tc.SPATIENTUID """ \
                       """    INNER JOIN BOM.RTPLAN rtplan ON rtplan.SCASEUID = tc.SUID """ \
                       """WHERE """ \
                       """    pt.SID = '%s' and tc.SLABEL = '%s'""" % (
                           patient, case) + imagestr + pubstring + plan_string
            # print querystr
            c1.execute(querystr)

            res = c1.fetchall()

        finally:
            c1.close()
    finally:
        db.close()

    return res


def write_file(data, filename ="RTSTRUCT.dcm"):
    """Write data to file"""
    file = open(filename, "wb")
    file.write(data)
    file.close()


def get_rtplan_from_id(patlist):
    """Return RT plan data for patients with IDs specified"""
    rpname = "RTPLAN.dcm"
    pat_dict = {}
    for patient in patlist:
        cases = get_patient_cases(patient)
        if len(cases) == 0:
            continue
        if patient not in pat_dict:
            pat_dict[patient] = {}
        for case in cases:
            rps = get_rtplan(patient, case)
            for rp in rps:
                if rp is None:
                    print
                    "(" + patient + "," + case + ") is (probably) filed to archive"
                    continue
                write_file(rp[1], rpname)
                if case not in pat_dict[patient]:
                    pat_dict[patient][case] = {}
                pat_dict[patient][case][rp[0]] = bes

                # house cleaning
    if os.path.isfile(rpname):
        os.remove(rpname)
    for patient in pat_dict:
        for case in pat_dict[patient]:
            for plan in pat_dict[patient][case]:
                print
                patient + "\t" + "%-15s" % case + '\t' + "%-15s" % plan
                for beam in pat_dict[patient][case][plan]:
                    outstr = ""
                    for el in beam:
                        outstr = outstr + "\t" + "%-8s" % el
                    print(outstr)


def string_list_to_float_list(slist, factor=1.0):
    """Convert list of strings to list of floats"""
    float_list = [float(s) * factor for s in slist]
    return float_list


def get_odbc_connection(
        svrName,
        dbName,
        usrName,
        drvr,
        portNum,
        pw='',
        readonlybool=True):
    """Returns ODBC connection"""

    if pw == '':
        print('empty pw')
        print('getpass does not work in spyder ide')
        # pwPrompt = 'Enter password for %(usr)s on %(svr)s (will not echo)' % {"usr": usrName, "svr": svrName}
        # print pwPrompt
        # ---- Getpass does not work in spyder IDE
        # pw=getpass.getpass(pwPrompt)

    cnxnStr = 'DRIVER={%(drvrStr)s};SERVER=%(svr)s;PORT=%(port)s;DATABASE=%(db)s;UID=%(usr)s;PWD=%(pw)s' % {
        "svr": svrName, "db": dbName, "usr": usrName, "pw": pw, "drvrStr": drvr, "port": portNum}
    # print cnxnStr

    try:
        cnxn = pyodbc.connect(cnxnStr, readonly=readonlybool)
        cnxn.cursor()  # just to try it, see if it works, catch failure here
    except pyodbc.Error:
        print(sys.exc_info())
        # ipshell=IPython.embed()
        # ipshell()

    return cnxn


def get_omp_connection(pw=''):
    """Returns ODBC connection to OTP database"""

    # Server, port, DB all come from DSN, so this is a bit misleading
    svrName = 'RQFH5SRVIPLANFL'
    dbName = 'OTP_Database'
    usrName = 'DBLOOK'
    drvr = 'MIMER'
    portNum = '1360'

    cnxn = get_odbc_connection(svrName, dbName, usrName, drvr, portNum, pw)

    return cnxn
