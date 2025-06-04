import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, text
import sys
from datetime import date
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_db_engine(db_info):
    """Create database engine based on database type"""
    db_type = db_info['db_type'].lower()
    
    try:
        if db_type in ['postgre', 'postgresql']:
            try:
                import psycopg2
                conn_str = f"postgresql+psycopg2://{db_info['username1']}:{db_info['password1']}@{db_info['host1']}/{db_info['database1']}"
            except ImportError:
                raise ImportError("psycopg2 is required for PostgreSQL connections. Install with: pip install psycopg2-binary")
                
        elif db_type in ['mysql', 'mysql_wh']:
            try:
                import pymysql
                if db_type == 'mysql':
                    port = db_info.get('port1', 3306)
                    conn_str = f"mysql+pymysql://{db_info['username1']}:{db_info['password1']}@{db_info['host1']}:{port}/{db_info['database1']}"
                else:  # mysql_wh
                    conn_str = f"mysql+pymysql://{db_info['username1']}:{db_info['password1']}@{db_info['host1']}/{db_info['database1']}"
            except ImportError:
                raise ImportError("pymysql is required for MySQL connections. Install with: pip install pymysql")
                
        elif db_type == 'sqlite':
            conn_str = f"sqlite:///{db_info['database1']}"
            
        else:
            raise ValueError(f"Unsupported database type: {db_type}. Supported types: mysql, postgresql, sqlite")
            
        return create_engine(conn_str)
        
    except Exception as e:
        logger.error(f"Failed to create engine for {db_type}: {str(e)}")
        raise

def fetch_credentials(metadata_engine, db_type):
    """Fetch database credentials from metadata database"""
    try:
        # Updated to match Django model field names
        query = f"""
            SELECT db_type, host1, port1, database1, username1, password1 
            FROM ETL_DATABASE_CRED
            WHERE LOWER(db_type) = LOWER('{db_type}')
            LIMIT 1
        """
        df = pd.read_sql(query, metadata_engine)
        if df.empty:
            raise ValueError(f"No credentials found for db_type: {db_type}")
        
        cred_dict = df.iloc[0].to_dict()
        logger.info(f"Successfully fetched credentials for database type: {db_type}")
        return cred_dict
        
    except Exception as e:
        logger.error(f"Failed to fetch credentials for {db_type}: {str(e)}")
        raise

def is_already_loaded(metadata_engine, srctbl_id):
    """Check if ETL has already been executed today for this source table"""
    try:
        today = date.today().isoformat()
        query = text("""
            SELECT 1 FROM EXECUTION_TRACK
            WHERE EXECUTION_DT = :today AND SRCTBL_ID = :srctbl_id AND COMPLETE_TRACK = 'Y'
            LIMIT 1
        """)
        with metadata_engine.connect() as conn:
            result = conn.execute(query, {"today": today, "srctbl_id": srctbl_id}).fetchone()
        return result is not None
    except Exception as e:
        logger.warning(f"Could not check execution status for SRCTBL_ID {srctbl_id}: {str(e)}")
        return False

def mark_as_loaded(metadata_engine, srctbl_id):
    """Mark the ETL process as completed for this source table"""
    try:
        today = date.today().isoformat()
        
        # Check if record exists
        check_query = text("""
            SELECT 1 FROM EXECUTION_TRACK
            WHERE EXECUTION_DT = :today AND SRCTBL_ID = :srctbl_id
        """)
        
        with metadata_engine.begin() as conn:
            existing = conn.execute(check_query, {"today": today, "srctbl_id": srctbl_id}).fetchone()
            
            if existing:
                # Update existing record
                update_query = text("""
                    UPDATE EXECUTION_TRACK 
                    SET COMPLETE_TRACK = 'Y'
                    WHERE EXECUTION_DT = :today AND SRCTBL_ID = :srctbl_id
                """)
                conn.execute(update_query, {"today": today, "srctbl_id": srctbl_id})
            else:
                # Insert new record
                insert_query = text("""
                    INSERT INTO EXECUTION_TRACK (EXECUTION_DT, SRCTBL_ID, COMPLETE_TRACK)
                    VALUES (:today, :srctbl_id, 'Y')
                """)
                conn.execute(insert_query, {"today": today, "srctbl_id": srctbl_id})
                
        logger.info(f"Marked SRCTBL_ID {srctbl_id} as completed for {today}")
        
    except Exception as e:
        logger.error(f"Failed to mark SRCTBL_ID {srctbl_id} as loaded: {str(e)}")
        # Don't raise here as the ETL might have succeeded even if we can't mark it

def check_dependencies():
    """Check if required dependencies are available"""
    missing_deps = []
    
    try:
        import pymysql
    except ImportError:
        missing_deps.append("pymysql (for MySQL connections)")
    
    # Only check for psycopg2 if we actually need it
    # We'll check this dynamically when creating engines
    
    if missing_deps:
        logger.warning(f"Missing optional dependencies: {', '.join(missing_deps)}")
        logger.info("Install missing dependencies as needed for your database connections")

def main(datasrc_id):
    """Main ETL execution function"""
    logger.info(f"Starting ETL process for DATASRC_ID: {datasrc_id}")
    
    # Check dependencies
    check_dependencies()
    
    try:
        # Connect to metadata database (Django database)
        try:
            import pymysql
            metadata_conn_str = "mysql+pymysql://RRPLDATA:$t06ngPa$$w0rd@192.168.2.76:3306/etl_db"
            metadata_engine = create_engine(metadata_conn_str)
        except ImportError:
            logger.error("pymysql is required for metadata database connection. Install with: pip install pymysql")
            sys.exit(1)
            
        logger.info("Connected to metadata database")

        # Test metadata connection
        try:
            with metadata_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except Exception as e:
            logger.error(f"Failed to connect to metadata database: {str(e)}")
            logger.error("Please check your database connection settings")
            sys.exit(1)

        # Get table information for the data source
        query = f"""
            SELECT * FROM ETL_TABLE_INFO 
            WHERE DATASRC_ID = {datasrc_id}
        """
        srctbl_info_df = pd.read_sql(query, metadata_engine)


        if srctbl_info_df.empty:
            logger.warning(f"No tables found for DATASRC_ID = {datasrc_id}")
            print(f"No tables found for DATASRC_ID = {datasrc_id}")
            return

        logger.info(f"Found {len(srctbl_info_df)} table(s) to process")
        success_count = 0
        error_count = 0

        for _, row in srctbl_info_df.iterrows():
            srctbl_id = row['SRCTBL_ID']
            
            try:
                # Check if already loaded today
                if is_already_loaded(metadata_engine, srctbl_id):
                    logger.info(f"Skipping SRCTBL_ID {srctbl_id} (already loaded today)")
                    print(f"⏭️  Skipping SRCTBL_ID {srctbl_id} (already loaded today)")
                    continue

                src_db_type = row['SRC_DATABASE']
                tgt_db_type = row['TGT_DATABASE']
                src_schema = row['SRC_SCHEMA']
                tgt_schema = row['TGT_SCHEMA']
                src_table = row['SRC_TABLENAME']
                tgt_table = row['TGT_TABLENAME']

                logger.info(f"Processing table: {src_schema}.{src_table} -> {tgt_schema}.{tgt_table}")

                # Get database credentials
                try:
                    src_cred = fetch_credentials(metadata_engine, src_db_type)
                    tgt_cred = fetch_credentials(metadata_engine, tgt_db_type)
                except Exception as e:
                    logger.error(f"Failed to fetch credentials: {str(e)}")
                    print(f"❌ Failed to fetch credentials for {src_db_type} or {tgt_db_type}: {str(e)}")
                    error_count += 1
                    continue

                # Create database engines
                try:
                    src_engine = get_db_engine(src_cred)
                    tgt_engine = get_db_engine(tgt_cred)
                except Exception as e:
                    logger.error(f"Failed to create database engines: {str(e)}")
                    print(f"❌ Database connection error: {str(e)}")
                    error_count += 1
                    continue

                # Handle schema and table name inference
                if tgt_schema and tgt_schema.upper() == 'INFER_SRC':
                    tgt_schema = src_schema.strip() if src_schema else None
                if tgt_table and tgt_table.upper() == 'INFER_SRC':
                    tgt_table = src_table.strip()

                # Build source query
                if src_schema:
                    src_query = f"SELECT * FROM {src_schema}.{src_table}"
                else:
                    src_query = f"SELECT * FROM {src_table}"

                logger.info(f"Executing source query: {src_query}")
                
                # Extract data from source
                try:
                    df = pd.read_sql(src_query, src_engine)
                    logger.info(f"Extracted {len(df)} rows from source")
                except Exception as e:
                    logger.error(f"Failed to extract data from source: {str(e)}")
                    print(f"❌ Source data extraction failed: {str(e)}")
                    error_count += 1
                    continue

                if df.empty:
                    logger.warning(f"No data found in source table {src_schema}.{src_table}")
                    print(f"⚠️  No data found in {src_schema}.{src_table}")
                    continue

                # Load data to target
                try:
                    df.to_sql(
                        name=tgt_table, 
                        con=tgt_engine, 
                        schema=tgt_schema, 
                        if_exists='replace', 
                        index=False,
                        method='multi',
                        chunksize=1000
                    )
                except Exception as e:
                    logger.error(f"Failed to load data to target: {str(e)}")
                    print(f"❌ Target data loading failed: {str(e)}")
                    error_count += 1
                    continue

                success_count += 1
                logger.info(f"Successfully loaded {len(df)} rows to {tgt_schema}.{tgt_table}")
                print(f"✅ Loaded {len(df)} rows from {src_schema}.{src_table} to {tgt_schema}.{tgt_table}")

                # Mark as completed
                mark_as_loaded(metadata_engine, srctbl_id)

                # Close connections for this iteration
                src_engine.dispose()
                tgt_engine.dispose()

            except Exception as e:
                error_count += 1
                error_msg = f"Error processing {src_schema}.{src_table}: {str(e)}"
                logger.error(error_msg)
                print(f"❌ {error_msg}")
                continue

        # Summary
        total_tables = len(srctbl_info_df)
        logger.info(f"ETL completed. Success: {success_count}, Errors: {error_count}, Total: {total_tables}")
        print(f"\n📊 ETL Summary for DATASRC_ID {datasrc_id}:")
        print(f"   ✅ Successful: {success_count}")
        print(f"   ❌ Errors: {error_count}")
        print(f"   📋 Total: {total_tables}")

    except Exception as e:
        error_msg = f"Fatal error in ETL process: {str(e)}"
        logger.error(error_msg)
        print(f"💥 {error_msg}")
        sys.exit(1)
    
    finally:
        # Clean up metadata connection
        try:
            metadata_engine.dispose()
        except:
            pass

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python load_table.py <DATASRC_ID>")
        print("Example: python load_table.py 1")
        sys.exit(1)

    try:
        datasrc_id = int(sys.argv[1])
    except ValueError:
        print("❌ Error: DATASRC_ID must be an integer.")
        sys.exit(1)

    if datasrc_id <= 0:
        print("❌ Error: DATASRC_ID must be a positive integer.")
        sys.exit(1)

    main(datasrc_id)