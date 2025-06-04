import pymysql

try:
    # Test exact Django connection
    conn = pymysql.connect(
        host='192.168.2.76',
        port=3306,
        user='RRPLDATA',
        password='$t06ngPa$$w0rd',
        database='etl'
    )
    print("✅ Python connection successful!")
    conn.close()
except Exception as e:
    print(f"❌ Python connection failed: {e}")