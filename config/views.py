from django.db import connection
from django.http import JsonResponse

def db_status(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT DATABASE(), VERSION()")
        database, version = cursor.fetchone()

    return JsonResponse({
        "application": "Django running on EC2-APP-01",
        "database_status": "Connected",
        "database_name": database,
        "mysql_version": version,
    })