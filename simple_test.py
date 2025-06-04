# simple_test.py
import pymysql
import sys

def test_step_by_step():
    """Test connection step by step to isolate the issue"""
    
    print("🔍 Testing MySQL Connection Step by Step")
    print("=" * 50)
    
    # Connection details
    host = '192.168.2.76'
    port = 3306
    user = 'RRPLDATA'
    password = '$t06ngPa$$w0rd'
    
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"User: {user}")
    print(f"Password: {password}")
    print("-" * 50)
    
    # Test 1: Basic connection without database
    print("\n1️⃣ Testing basic connection (no database)...")
    try:
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            autocommit=True
        )
        
        cursor = connection.cursor()
        cursor.execute("SELECT 'Connection successful' as status")
        result = cursor.fetchone()
        print(f"✅ Basic connection: {result[0]}")
        
        # Show available databases
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        db_list = [db[0] for db in databases]
        print(f"📋 Available databases: {db_list}")
        
        # Check if etl exists
        if 'etl' in db_list:
            print("✅ etl already exists!")
            etl_exists = True
        else:
            print("❌ etl does not exist - we'll create it")
            etl_exists = False
        
        cursor.close()
        connection.close()
        
        return etl_exists
        
    except Exception as e:
        print(f"❌ Basic connection failed: {e}")
        print("\n💡 This usually means:")
        print("   - Wrong IP address or port")
        print("   - Wrong username or password")
        print("   - MySQL server not running")
        print("   - Firewall blocking connection")
        return None

def create_database():
    """Create the etl database"""
    print("\n2️⃣ Creating etl database...")
    
    try:
        connection = pymysql.connect(
            host='192.168.2.76',
            port=3306,
            user='RRPLDATA',
            password='$t06ngPa$$w0rd',
            autocommit=True
        )
        
        cursor = connection.cursor()
        
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS etl CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print("✅ Database created/verified!")
        
        # Verify it exists
        cursor.execute("SHOW DATABASES LIKE 'etl'")
        result = cursor.fetchone()
        if result:
            print("✅ etl confirmed to exist")
        else:
            print("❌ etl creation failed")
            return False
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Database creation failed: {e}")
        print("\n💡 This usually means:")
        print("   - User doesn't have CREATE DATABASE privileges")
        print("   - Database name conflicts")
        return False

def test_database_connection():
    """Test connection to etl database"""
    print("\n3️⃣ Testing connection to etl...")
    
    try:
        # Method 1: Direct specification
        connection = pymysql.connect(
            host='192.168.2.76',
            port=3306,
            user='RRPLDATA',
            password='$t06ngPa$$w0rd',
            database='etl',
            charset='utf8mb4',
            autocommit=True
        )
        
        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE() as current_db, USER() as current_user")
        result = cursor.fetchone()
        print(f"✅ Connected to database: {result[0]}")
        print(f"✅ Connected as user: {result[1]}")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_sqlalchemy():
    """Test SQLAlchemy connection"""
    print("\n4️⃣ Testing SQLAlchemy connection...")
    
    try:
        from sqlalchemy import create_engine, text
        
        # Simple connection string without encoding
        conn_str = "mysql+pymysql://RRPLDATA:$t06ngPa$$w0rd@192.168.2.76:3306/etl"
        print(f"Connection string: mysql+pymysql://RRPLDATA:***@192.168.2.76:3306/etl")
        
        engine = create_engine(conn_str, echo=False)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT DATABASE(), USER(), NOW()"))
            row = result.fetchone()
            print(f"✅ SQLAlchemy connection successful!")
            print(f"   Database: {row[0]}")
            print(f"   User: {row[1]}")
            print(f"   Server time: {row[2]}")
        
        return True
        
    except Exception as e:
        print(f"❌ SQLAlchemy connection failed: {e}")
        print(f"   Full error: {str(e)}")
        return False

def create_tables():
    """Create required tables"""
    print("\n5️⃣ Creating required tables...")
    
    try:
        connection = pymysql.connect(
            host='192.168.2.76',
            port=3306,
            user='RRPLDATA',
            password='$t06ngPa$$w0rd',
            database='etl',
            autocommit=True
        )
        
        cursor = connection.cursor()
        
        # Create EXECUTION_TRACK table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS EXECUTION_TRACK (
            EXECUTION_DT DATE NOT NULL,
            SRCTBL_ID INT NOT NULL,
            COMPLETE_TRACK CHAR(1) DEFAULT 'N',
            CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UPDATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (EXECUTION_DT, SRCTBL_ID),
            INDEX idx_execution_dt (EXECUTION_DT),
            INDEX idx_srctbl_id (SRCTBL_ID)
        )
        """
        
        cursor.execute(create_table_sql)
        print("✅ EXECUTION_TRACK table created/verified!")
        
        # Show tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        table_list = [table[0] for table in tables]
        print(f"📋 Tables in etl: {table_list}")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ Table creation failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ETL System - Simple Connection Diagnostic")
    print("=" * 60)
    
    # Test basic connection
    etl_exists = test_step_by_step()
    
    if etl_exists is None:
        print("\n❌ Cannot connect to MySQL server. Please check:")
        print("1. Server IP: 192.168.2.76")
        print("2. Username: RRPLDATA")
        print("3. Password: $t06ngPa$$w0rd")
        print("4. MySQL server is running")
        print("5. Port 3306 is accessible")
        sys.exit(1)
    
    # Create database if it doesn't exist
    if not etl_exists:
        if not create_database():
            print("\n❌ Cannot create database. Check user permissions.")
            sys.exit(1)
    
    # Test database connection
    if not test_database_connection():
        print("\n❌ Cannot connect to etl database.")
        sys.exit(1)
    
    # Test SQLAlchemy
    if not test_sqlalchemy():
        print("\n❌ SQLAlchemy connection failed.")
        sys.exit(1)
    
    # Create tables
    if not create_tables():
        print("\n❌ Cannot create required tables.")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED!")
    print("✅ MySQL server connection working")
    print("✅ etl database ready")
    print("✅ SQLAlchemy connection working")
    print("✅ Required tables created")
    print("=" * 60)
    
    print("\n🎯 Next steps:")
    print("1. Your database is ready!")
    print("2. Run: python manage.py migrate")
    print("3. Run: python manage.py init_etl_system")
    print("4. Run: python manage.py runserver")