from o2x5xx import O2x5xxDevice
import pyodbc

device = O2x5xxDevice(address='192.168.0.69', port=50010)

# Trusted connection to named instance
connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                            'SERVER=localhost\SQLEXPRESS;'
                            'DATABASE=O2I5xx_code_reading;'
                            'Trusted_Connection=yes;')

cursor = connection.cursor()

while True:
    # This is an example and is working for an incoming string like: station_1;1234567890
    print('Waiting for next incoming data from sensor ...')
    _, answer = device.read_next_answer()

    station = answer.decode().split(';')[0]
    code = answer.decode().split(';')[1]

    if code:
        try:
            sql_insert_query = "INSERT INTO dbo.codes (code, station) VALUES ('{code}','{station}')"\
                .format(code=code, station=station)
            cursor.execute(sql_insert_query)
            cursor.commit()

            print('Code successfully written to DB.')
        except pyodbc.ProgrammingError:
            print('Unable to write to DB!')
    else:
        print("No code found!")
