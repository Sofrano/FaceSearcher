import psycopg2


def setup_db():
    dbconnection = psycopg2.connect("user='' password='' host='localhost' dbname=''")
    db=dbconnection.cursor()
    #db.execute("create extension if not exists cube;") this should be run as postgres user
    db.execute("drop table if exists vectors")
    db.execute("create table vectors (id serial, file varchar, vec_low cube, vec_high cube, imagepath varchar, sourceid smallint, username varchar, link varchar );")
    db.execute("create index vectors_vec_idx on vectors (vec_low, vec_high);")


setup_db()
