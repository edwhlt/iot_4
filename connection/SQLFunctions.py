import sqlite3
import time
from datetime import datetime


def loadFromDB(scenarioTable):
    try:
        conn = sqlite3.connect("../iot.sqlite")
        # conn = psycopg2.connect(database="iot", user="iot", password="iot", host="pi", port="5432")
        cursor = conn.cursor()
        cursor.execute("SELECT name, begin, \"end\" FROM scenarios")
        data = cursor.fetchall()

        # Populate the QTableWidget with the retrieved data
        scenarioTable.setRowCount(len(data))
        for row_index, row_data in enumerate(data):
            print(row_data)
            scenarioTable.addRow(row_index, row_data[0], row_data[1], row_data[2])

        # Close the connection
        conn.close()
    except Exception as e:
        print(f"Error: {str(e)}")


def createTableIfNotExists():
    try:
        conn = sqlite3.connect("../iot.sqlite")
        cursor = conn.cursor()

        # Create a table if it doesn't exist
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS scenarios (id SERIAL PRIMARY KEY, name VARCHAR(255) NOT NULL, begin INTEGER, \"end\" INTEGER, timestamp TIMESTAMP NOT NULL)")

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error: {str(e)}")


def saveToDB(tableWidget):
    try:
        conn = sqlite3.connect("../iot.sqlite")
        # conn = psycopg2.connect(database="iot", user="iot", password="iot", host="pi", port="5432")
        cursor = conn.cursor()

        # Clear all rows from the 'scenarios' table
        cursor.execute('DELETE FROM scenarios')

        new_values = []

        # Iterate through the rows in the tableWidget
        for row in range(tableWidget.rowCount()):
            name = tableWidget.item(row, 0).text()
            begin = tableWidget.item(row, 1).text()
            end = tableWidget.item(row, 2).text()
            timestamp = time.time()  # Get the current timestamp

            # Append the values as a tuple to the new_values list
            new_values.append((name, begin, end, timestamp))

        # Insert the new values into the 'scenarios' table
        cursor.executemany(
            "INSERT INTO scenarios (name, begin, end, timestamp) VALUES (?, ?, ?, ?)",
            new_values
        )
        # Commit changes and close the connection
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error: {str(e)}")


def saveValuesMQTT(message):
    try:
        payload = message.payload.decode("utf-8")
        timestamp = datetime.now()
        conn = sqlite3.connect("../iot.sqlite")
        cursor = conn.cursor()

        cursor.execute(
            "CREATE TABLE IF NOT EXISTS mqtt_data (id SERIAL PRIMARY KEY, topic VARCHAR(255) NOT NULL, payload TEXT, "
            "timestamp TIMESTAMP NOT NULL);")

        cursor.execute(
            "INSERT INTO mqtt_data (topic, payload, timestamp) VALUES (?, ?, ?)",
            (message.topic, payload, timestamp)
        )
        conn.commit()
        conn.close()

    except Exception as e:
        print(f"Error: {str(e)}")