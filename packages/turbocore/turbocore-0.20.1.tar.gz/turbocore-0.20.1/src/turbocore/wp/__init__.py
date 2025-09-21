import turbocore
import turbocore.wp.sshtooled


def turbo_wpcli_mysql(HOST, MYSQLUSER, MYSQLPW, DB, SQL):
    x = turbocore.wp.sshtooled.get_mysql_tsv(HOST, MYSQLUSER, MYSQLPW, DB, SQL)
    print(x)


def main():
    turbocore.cli_this(__name__, 'turbo_wpcli_')
