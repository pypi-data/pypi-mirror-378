import pytest
from antarpy_dao.AntarpyNeo4jDatasource import AntarpyNeo4jDatasource
from antarpy_dao.AntarpyNeo4jRetryPolicy import AntarpyNeo4jRetryPolicy
from antarpy_dao.AntarpyNeo4jSession import AntarpyNeo4jSession
from neo4j import Session
from neo4j.exceptions import SessionExpired, ClientError
import os
import logging
import json
import time
import threading
import pandas as pd
from pandas.api.types import (
    is_integer_dtype,
    is_float_dtype,
    is_object_dtype,
)
#logger = logging.getLogger(__name__)
#logger.setLevel(logging.DEBUG)

# Add a console handler (stdout)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Attach handler if not already attached
#if not logger.hasHandlers():
#    logger.addHandler(console_handler)

#logging.getLogger("neo4j").setLevel(logging.WARNING)

dbUser=os.environ["DBUSERNAME"]
dbPwd=os.environ["DBPASSWORD"]
dbHost=os.environ["DBHOSTNAME"]
dbPort=os.environ["DBPORT"]
dbDb=os.environ["DBDATABASE"]

# Shared connection details
CONN_DETAILS = {
    "con_type": "neo4j",
    "con_hostname": dbHost,
    "con_port": dbPort,
    "con_username": dbUser,
    "con_password": dbPwd,
    "con_database": "neo4j"
}

# Create object once
neo4j_datasource = AntarpyNeo4jDatasource()

def get_test_db_connection():
    ds = neo4j_datasource
    ds.init_dao(CONN_DETAILS.copy())
    ds.connect()
    return ds

def print_msg(msg):
    print("\n\n####################################################")
    print(f"           {msg}")
    print("####################################################\n")

def test_section_dao_init():
    print_msg("Initialisation")
    assert True

def test_init_dao_sets_connection_details():
    ds = AntarpyNeo4jDatasource()
    ds.init_dao(CONN_DETAILS.copy())
    assert ds.con_details["connected"] is False

def test_connect_and_disconnect():
    ds = get_test_db_connection()
    assert ds.driver is not None
    assert ds.is_connected() is True

    ds.disconnect()
    assert ds.driver is None
    assert ds.is_connected() is False

# Test connecting to multiple databases.
def test_multiple_database_connections():
    ds = get_test_db_connection()

    # Connect to default DB
    result = ds.query("CALL db.info() YIELD name RETURN name")
    db_name = result[0]["name"]
    assert db_name == CONN_DETAILS["con_database"]

    # Connect to system - always there
    result = ds.query("CALL db.info() YIELD name RETURN name",database="system")
    db_name = result[0]["name"]
    assert db_name == "system"

    ds.close()

def test_section_parameters():
    print_msg("Parameter tests")
    assert True

def test_validate_params_valid():
    ds = AntarpyNeo4jDatasource()
    params = {"a": 1, "b": "str", "c": 1.56, "d": True}
    ds._validate_params(params)


@pytest.mark.parametrize("bad_params", [
    ["not", "a", "dict"],
    "value",
    object()
])
def test_validate_params_invalid(bad_params):
    ds = AntarpyNeo4jDatasource()
    with pytest.raises(Exception):
        ds._validate_params(bad_params)

# Execute Update and Query with Parameters - default    
def test_execute_update_with_parameters():
    ds = get_test_db_connection()

    # Cleanup Old Data
    cleanup = ds.get_dao_write_session()
    cleanup.begin()
    #ds.update("MATCH (n:TestNode) DELETE n", dao_session=cleanup)
    cleanup.update("MATCH (n:TestNode) DELETE n")
    cleanup.commit()
    cleanup.close()

    params = {"name": "jeremy", "age": 54}
    ds.update("MERGE (n:TestNode {name: $name, age: $age})",params=params)
    result = ds.query("MATCH (n:TestNode {name: $name, age: $age}) return count(n) as cnt", params=params)
    val = result[0]["cnt"]
    assert val == 1

    # Cleanup Old Data
    cleanup = ds.get_dao_write_session()
    cleanup.begin()
    #ds.update("MATCH (n:TestNode) DELETE n", dao_session=cleanup)
    cleanup.update("MATCH (n:TestNode) DELETE n")
    cleanup.commit()
    cleanup.close()

    ds.close()

def test_execute_session_update_with_parameters():
    ds = get_test_db_connection()

    # Cleanup Old Data
    cleanup = ds.get_dao_write_session()
    cleanup.begin()
    #ds.update("MATCH (n:TestNode) DELETE n", dao_session=cleanup)
    cleanup.update("MATCH (n:TestNode) DELETE n")
    cleanup.commit()
    cleanup.close()

    dao_session= ds.get_dao_write_session()
    params = {"name": "jeremy", "age": 54}
    dao_session.begin()
    #ds.update("MERGE (n:TestNode {name: $name, age: $age})",params=params,dao_session=dao_session)
    dao_session.update("MERGE (n:TestNode {name: $name, age: $age})",params=params)
    dao_session.commit()

    #result = ds.query("MATCH (n:TestNode {name: $name, age: $age}) return count(n) as cnt", params=params,dao_session=dao_session)
    result = dao_session.query("MATCH (n:TestNode {name: $name, age: $age}) return count(n) as cnt", params=params)
    val = result[0]["cnt"]
    assert val == 1
    dao_session.close()

    # Cleanup Old Data
    cleanup = ds.get_dao_write_session()
    cleanup.begin()
    #ds.update("MATCH (n:TestNode) DELETE n", dao_session=cleanup)
    cleanup.update("MATCH (n:TestNode) DELETE n")
    cleanup.commit()
    cleanup.close()

    ds.close()

# Test Return Types (result_transformer)
@pytest.mark.filterwarnings("ignore:Expected a result with a single record, but found multiple.")
def test_result_transformers():
    ds = get_test_db_connection()

    cypher_qry = 'show databases YIELD name where name = "system" RETURN count(*) as cnt'
    
    #  Single
    cnt = ds.query(cypher_qry,format="SINGLE")
    assert 1 == cnt

    # Test return Single on Multiple
    name = ds.query('show databases YIELD name WHERE name in ["system", "neo4j"] RETURN name ORDER BY name desc', format="SINGLE")
    assert name == "system"
    
    # Test return Single on None.
    name = ds.query('show databases YIELD name where name = "noname123" RETURN name', format="SINGLE")
    assert not name

    # List - LIST of neo4j RECORDS
    result = ds.query(cypher_qry,format="LIST")
    assert 1 == result[0].value("cnt")

    # DICT - List of DICT's
    result = ds.query(cypher_qry,format="DICT")
    assert 1 == result[0]["cnt"]  

    # Test Return Node
    my_dict = {"name":"Jeremy",  "age":54, "height":"182"}
    ds.update("MERGE (t:TestNode {name:$name}) SET t.age=$age, t.height=$height", my_dict)
    result = ds.query("MATCH (t:TestNode {name:$name}) return t", my_dict, format="SINGLE")
    assert isinstance(result, dict)

    ds.update("MATCH (t:TestNode {name:$name}) detach delete t", my_dict)
    cnt = ds.query("MATCH (t:TestNode {name:$name}) return count(t) as cnt", my_dict, format="SINGLE")
    assert cnt == 0

    # RECORD 
    dao_session = ds.get_dao_read_session()
    dao_session.begin()
    #result = ds.query(cypher_qry,dao_session=dao_session,format="RECORD")
    result = dao_session.query(cypher_qry, format="RECORD")
    assert result.single().value("cnt") == 1
    dao_session.rollback()
    dao_session.close()
    
    # Dataframe
    df = ds.query(cypher_qry,format="DATAFRAME")    
    assert df.shape == (1, 1)
    assert df.columns.tolist() == ["cnt"]
    assert df.iloc[0]["cnt"] == 1    

    # JSON
    result = ds.query(cypher_qry, format="JSON")
    data = json.loads(result)
    assert isinstance(data, dict)
    assert data["json"][0]["cnt"] == 1 

    # CUSTOM
    result = ds.query(cypher_qry,format="CUSTOM", result_xform=lambda r: r.single().value("cnt"))    
    assert result == 1

    #CUSTOM gets result and summary, works under both query and update.
    ds.update("MATCH (t:Test) detach delete t")
    cypher_stmt = """
             MERGE (t:Test  {id:'1'})
             MERGE (t1:Test {id:'2'})
             WITH t,t1
             MATCH (t2:Test)
             RETURN t2.id as id
             ORDER BY t2.id asc
         """
    result = ds.update(cypher_stmt,format="CUSTOM", result_xform=lambda r: r.single().value("id"))    
    assert result == '1'
    ds.update("MATCH (t:Test) detach delete t")
    ds.close()


def test_query_returns_dataframe_with_expected_schema_and_dtypes():
    ds = get_test_db_connection()

    # Clean slate for this label (safe if none exist)
    ds.update("MATCH (n:DFTest) DETACH DELETE n")

    # Insert a few rows using your batch update path (list[dict] → _batch_update)
    rows = [
        {"id": 1, "name": "Alice", "age": 30, "height": 1.70},
        {"id": 2, "name": "Bob",   "age": 41, "height": 1.83},
        {"id": 3, "name": "Cara",  "age": 25, "height": 1.62},
    ]
    ds.update(
        "MERGE (n:DFTest {id: $id}) "
        "SET n.name = $name, n.age = $age, n.height = $height",
        rows
    )

    # Query as a DataFrame (this exercises your DATAFRAME transformer path)
    df = ds.query(
        "MATCH (n:DFTest) "
        "RETURN n.id AS id, n.name AS name, n.age AS age, n.height AS height "
        "ORDER BY id",
        format="DATAFRAME",
    )

    # Basic shape checks
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert list(df.columns) == ["id", "name", "age", "height"]
    assert len(df) == 3

    # Dtype checks (schema semantics, not exact numpy dtype names)
    assert is_integer_dtype(df["id"])
    assert is_object_dtype(df["name"])     # strings → object dtype
    assert is_integer_dtype(df["age"])
    assert is_float_dtype(df["height"])    # heights are floats

    # Optional: quick content sanity
    assert df.iloc[0].to_dict() == {"id": 1, "name": "Alice", "age": 30, "height": 1.70}

    # Cleanup (keeps the graph tidy for other tests)
    ds.update("MATCH (n:DFTest) DETACH DELETE n")
    ds.close()


def test_section_query_update():

    print_msg("Query/Update tests")
    assert True

def test_executeQuery_on_live_instance():
    ds = get_test_db_connection()

    # Minimal query that works with empty DB
    result = ds.query("RETURN 1 AS num")
    assert result[0]["num"] == 1

    ds.disconnect()


def test_executeUpdate_on_live_instance():
    ds = get_test_db_connection()

    # Safe test node creation
    create_result = ds.update("CREATE (n:TestNode {name: 'pytest'}) RETURN n")
    assert create_result is not None
    assert len(create_result) == 1

    # Cleanup
    ds.update("MATCH (n:TestNode {name: 'pytest'}) DELETE n")
    ds.disconnect()


def test_str_representation():
    ds = AntarpyNeo4jDatasource()
    ds.init_dao(CONN_DETAILS.copy())
    assert str(ds) == str(ds.con_details)    


def test_apoc_iterate_via_update():
    cypher_qry = """
        CALL apoc.periodic.iterate(
            "MATCH (t:TestNode) RETURN t",
            "DETACH DELETE t",
            {batchSize: 10, parallel: false}
        )
    """
    ds = get_test_db_connection()
    try:
        ds.update(cypher_qry)
    except Exception as e:
        error_msg = str(e)
    
    assert error_msg == "Please use batch_update_APOC for apoc.periodic.iterate operations."

    ds.close()

def test_apoc_parameters():

    cypher_qry = """
        CALL apoc.periodic.iterate(
            "MATCH (t:TestNode) RETURN t",
            "DETACH DELETE t",
            {batchSize: 10, parallel: false}
        )
    """
    ds = AntarpyNeo4jDatasource()
    ds.init_dao(CONN_DETAILS.copy())
    try:
        ds.batch_update_APOC(cypher_qry)
    except Exception as e:
        error_msg = str(e)

    assert error_msg == "Not connected to a Database Instance"

    ds = get_test_db_connection()    
    try:
        ds.batch_update_APOC(cypher_qry,data_list="Hello")
    except Exception as e:
        error_msg = str(e)
    
    assert error_msg == "data_list parameter must be of type List"

    try:
        ds.batch_update_APOC(cypher_qry,data_list=["Hello"])
    except Exception as e:
        error_msg = str(e)        
    
    assert error_msg == "data_list contents must be of type Dict"

    ds.close()    

def test_apoc_iterate_contained():    
    cypher_qry = """
        CALL apoc.periodic.iterate(
            "MATCH (t:TestNode) RETURN t",
            "DETACH DELETE t",
            {batchSize: 10, parallel: false}
        )
    """
    ds = get_test_db_connection()    
    result = ds.batch_update_APOC(cypher_qry)
    assert result[0]["batches"] == 1

    ds.close()

def test_apoc_iterate_datalist_predefined():
    cypher_qry = """
        CALL apoc.periodic.iterate(
            "UNWIND $myList AS row RETURN row",
            "MERGE (t:TestNode {id: row.name})
             SET t.age = row.age",
            {params: {myList: $myList}, batchSize: 10, parallel: false}
        )
    """
    alist = [
        {"name":"Jeremy",  "age":54},
        {"name":"Cameron", "age":24}
    ]
    ds = get_test_db_connection()    
    result = ds.batch_update_APOC(cypher_qry, data_list=alist, apoc_data_list_name="myList")
    assert result[0]["batches"] == 1

    # Cleanup - apoc method - predefined
    result = ds.batch_update_APOC("""CALL apoc.periodic.iterate("MATCH (t:TestNode) RETURN t","DETACH DELETE t",{batchSize: 10, parallel: false})""")
    assert result[0]["operations"]["total"] == 2
    ds.close()

def test_apoc_iterate_datalist_parameter():
    cypher_qry = """ "MERGE (t:TestNode {id: row.name}) SET t.age = row.age", """
    alist = [
        {"name":"Jeremy",  "age":54},
        {"name":"Cameron", "age":24},
        {"name":"Natasha", "age":21},
    ]
    ds = get_test_db_connection()    
    result = ds.batch_update_APOC(cypher_qry, data_list=alist)
    assert result[0]["batches"] == 1

    # Cleanup - apoc method - not defined
    result = ds.batch_update_APOC(""" "MATCH (t:TestNode) RETURN t","DETACH DELETE t", """, trans_size=5)
    assert result[0]["operations"]["total"] == 3   
    ds.close()

def test_apoc_datalist_size_constraints():
    cypher_qry = ' "MERGE (t:TestNode {id: row.name}) SET t.age = row.age", '
    alist = [
        {"name":"Jeremy",  "age":54},
        {"name":"Cameron", "age":24},
        {"name":"Natasha", "age":21},
    ]    
    
    ds = get_test_db_connection() 

    # Test chunking of data
    ds.con_details["batch_limit"] = 2
    result = ds.batch_update_APOC(cypher_qry,data_list=alist, trans_size=3)
    assert len(result) == 2

    ds.close()

def test_CICT_iterate_datalist_parameter():
    cypher_qry = "MERGE (t:TestNode {id: row.name}) SET t.age = row.age"
    alist = [
        {"name":"Jeremy",  "age":54},
        {"name":"Cameron", "age":24},
        {"name":"Natasha", "age":21},
    ]
    ds = get_test_db_connection()    
    result = ds.batch_update_CICT(cypher_qry, data_list=alist)
    cnt = ds.query("MATCH (t:TestNode) return count(t) as cnt", format="SINGLE")
    assert cnt == 3

    # Cleanup  - Test no data_list    
    result = ds.batch_update_CICT("MATCH (t:TestNode) DETACH DELETE t",trans_size=5)
    cnt = ds.query("MATCH (t:TestNode) return count(t) as cnt", format="SINGLE")
    assert cnt == 0

    result = ds.batch_update_CICT(cypher_qry, data_list=alist,trans_size=1, parallel=True, threads=3)
    cnt = ds.query("MATCH (t:TestNode) return count(t) as cnt", format="SINGLE")
    assert cnt == 3

    result = ds.batch_update_CICT("MATCH (t:TestNode) DETACH DELETE t",trans_size=5)
    cnt = ds.query("MATCH (t:TestNode) return count(t) as cnt", format="SINGLE")
    assert cnt == 0

    ds.close()    

def test_CICT_on_error():
    cypher_qry = "MERGE (t:TestNode {id: row.name}) SET t.age = 10/row.age"
    alist = [
        {"name":"Jeremy",  "age":54},
        {"name":"Cameron", "age":24},
        {"name":"Natasha", "age":0},
    ]
    ds = get_test_db_connection() 

    # Ensure clean DN to start with
    ds.update("MATCH (t:TestNode) DETACH DELETE t")
    cnt = ds.query("MATCH (t:TestNode) where t.name in ['Jeremy', 'Cameron', 'Natasha'] return count(*) as cnt",format="SINGLE")

    
    # failures on_error CONTINUE will fail the entire transaction batch but will let the next batch through.
    result = ds.batch_update_CICT(cypher_qry, data_list=alist,on_error="CONTINUE")
    cnt = ds.query("MATCH (t:TestNode) return count(t) as cnt", format="SINGLE")
    assert cnt == 0

    # Split in to 3 threads
    #  - ON ERROR CONTINUE does not throw exception
    #  - 2 commit 1 fail
    #  - result has error message
    result = ds.batch_update_CICT(cypher_qry, data_list=alist, on_error="CONTINUE", trans_size=1,threads=3, parallel=True)
    count_error_mesg = 0
    for qry_log in result:
        if qry_log["s"]["errorMessage"] == "/ by zero":
            count_error_mesg += 1

    cnt = ds.query("MATCH (t:TestNode) return count(t) as cnt", format="SINGLE")
    assert cnt == 2
    assert count_error_mesg == 1

    # Cleanup
    ds.batch_update_CICT("MATCH (t:TestNode) DETACH DELETE t")
    cnt = ds.query("MATCH (t:TestNode) where t.name in ['Jeremy', 'Cameron', 'Natasha'] return count(*) as cnt",format="SINGLE")
    assert cnt == 0

    # Split in to 3 threads
    #  - ON ERROR BREAK does not throw exception
    #  - 2 commit 1 fail
    #  - result has error message
    result = ds.batch_update_CICT(cypher_qry, data_list=alist, on_error="BREAK", trans_size=1,threads=3, parallel=True)
    count_error_mesg = 0
    for qry_log in result:
        if qry_log["s"]["errorMessage"] == "/ by zero":
            count_error_mesg += 1

    cnt = ds.query("MATCH (t:TestNode) return count(t) as cnt", format="SINGLE")
    assert cnt == 2
    assert count_error_mesg == 1

    # Cleanup
    ds.batch_update_CICT("MATCH (t:TestNode) DETACH DELETE t")
    cnt = ds.query("MATCH (t:TestNode) where t.name in ['Jeremy', 'Cameron', 'Natasha'] return count(*) as cnt",format="SINGLE")
    assert cnt == 0
    

    # Split in to 3 threads 
    #  - ON ERROR FAIL throws Exception
    #  - 2 commit 1 fail
    error_msg = ""
    try:
        result = ds.batch_update_CICT(cypher_qry, data_list=alist, on_error="FAIL" , threads=3, parallel=True,trans_size=1)
    except Exception as e:
        error_msg = str(e)

    cnt = ds.query("MATCH (t:TestNode) return count(t) as cnt", format="SINGLE")
    assert cnt == 2
    assert "ArithmeticError" in error_msg
         

    # Cleanup
    ds.batch_update_CICT("MATCH (t:TestNode) DETACH DELETE t")
    cnt = ds.query("MATCH (t:TestNode) where t.name in ['Jeremy', 'Cameron', 'Natasha'] return count(*) as cnt",format="SINGLE")
    assert cnt == 0

    # Process in 3 transactions
    result = ds.batch_update_CICT(cypher_qry, data_list=alist,on_error="CONTINUE", parallel=False,trans_size=1)
    cnt = ds.query("MATCH (t:TestNode) return count(t) as cnt", format="SINGLE")
    assert cnt == 2

    # Cleanup
    ds.batch_update_CICT("MATCH (t:TestNode) DETACH DELETE t")
    cnt = ds.query("MATCH (t:TestNode) where t.name in ['Jeremy', 'Cameron', 'Natasha'] return count(*) as cnt",format="SINGLE")
    assert cnt == 0

    error_msg = ""
    try:
        result = ds.batch_update_CICT("MATCHS (t:TestNode) DETACH DELETE t")
    except Exception as e:
        error_msg = str(e)
    assert "SyntaxError" in error_msg

    ds.close()      

def test_batch_update_default_session():
    cypher_qry = "MERGE (t:TestNode {name: $name}) SET t.age = $age"
    alist = [
        {"name":"Jeremy",  "age":54},
        {"name":"Cameron", "age":24},
        {"name":"Natasha", "age":21},
    ]
    ds = get_test_db_connection()

    ds.update(cypher_qry, params=alist,trans_size=2)
    cnt = ds.query("MATCH (t:TestNode) where t.name in ['Jeremy', 'Cameron', 'Natasha'] return count(*) as cnt",format="SINGLE")
    assert cnt == 3

    # Cleanup
    ds.update("MATCH (t:TestNode) DETACH DELETE t")
    cnt = ds.query("MATCH (t:TestNode) where t.name in ['Jeremy', 'Cameron', 'Natasha'] return count(*) as cnt",format="SINGLE")
    assert cnt == 0
    ds.close()

def test_batch_update_manual_session():
    cypher_qry = "MERGE (t:TestNode {name: $name}) SET t.age = $age"
    alist = [
        {"name":"Jeremy",  "age":54},
        {"name":"Cameron", "age":24},
        {"name":"Natasha", "age":21},
    ]

    ds = get_test_db_connection()
    dao_session = ds.get_dao_write_session()
    #ds.update(cypher_qry, dao_session=dao_session,params=alist,trans_size=2)
    dao_session.update(cypher_qry,params=alist,trans_size=2 )
    #cnt = ds.query("MATCH (t:TestNode) where t.name in ['Jeremy', 'Cameron', 'Natasha'] return count(*) as cnt",dao_session=dao_session,format="SINGLE")
    cnt = dao_session.query("MATCH (t:TestNode) where t.name in ['Jeremy', 'Cameron', 'Natasha'] return count(*) as cnt",format="SINGLE")
    assert cnt == 3

    # Cleanup 
    ds.update("MATCH (t:TestNode) DETACH DELETE t")
    #cnt = ds.query("MATCH (t:TestNode) where t.name in ['Jeremy', 'Cameron', 'Natasha'] return count(*) as cnt",dao_session=dao_session,format="SINGLE")
    cnt = dao_session.query("MATCH (t:TestNode) where t.name in ['Jeremy', 'Cameron', 'Natasha'] return count(*) as cnt",format="SINGLE")

    assert cnt == 0

    dao_session.close()
    ds.close()



def test_section_transaction():

    print_msg("Transaction tests")
    assert True

def test_begin_and_commit_transaction():
    ds = get_test_db_connection()

    # Cleanup Old Data
    cleanup = ds.get_dao_write_session()
    cleanup.begin()
    #ds.update("MATCH (n:TestNode {name: 'zeta'}) DELETE n", dao_session=cleanup)
    cleanup.update("MATCH (n:TestNode {name: 'zeta'}) DELETE n")
    cleanup.commit()
    cleanup.close()

    # Create node in explicit transaction
    dao_session = ds.get_dao_write_session()
    dao_session.begin()
    #result = ds.update("CREATE (n:TestNode {name: 'zeta'}) RETURN n", dao_session=dao_session)
    result = dao_session.update("CREATE (n:TestNode {name: 'zeta'}) RETURN n")
    dao_session.commit()
    dao_session.close()

    assert len(result) == 1
    assert dao_session.is_in_txn is False
    
    # Check node exists using a new session
    verify_session = ds.get_dao_session()
    #check = ds.query("MATCH (n:TestNode {name: 'zeta'}) RETURN n", dao_session=verify_session)
    check = verify_session.query("MATCH (n:TestNode {name: 'zeta'}) RETURN n")
    assert len(check) == 1
    verify_session.close()

    # Cleanup
    cleanup = ds.get_dao_write_session()
    cleanup.begin()
    #ds.update("MATCH (n:TestNode {name: 'zeta'}) DELETE n", dao_session=cleanup)
    cleanup.update("MATCH (n:TestNode {name: 'zeta'}) DELETE n")
    cleanup.commit()
    cleanup.close()

    ds.disconnect()
    

def test_begin_and_rollback_transaction():
    ds = get_test_db_connection()
    dao_session = ds.get_dao_write_session()

    dao_session.begin()
    #ds.update("CREATE (n:TestNode {name: 'temp'}) RETURN n", dao_session=dao_session)
    dao_session.update("CREATE (n:TestNode {name: 'temp'}) RETURN n")
    dao_session.rollback()
    dao_session.close()

    # Use a new session to verify rollback
    verify = ds.get_dao_session()
    #result = ds.query("MATCH (n:TestNode {name: 'temp'}) RETURN n", dao_session=verify)
    result = verify.query("MATCH (n:TestNode {name: 'temp'}) RETURN n")
    assert result == []  # node should not exist
    verify.close()

    ds.disconnect()

# Session no longer raises exception on unresolved transaction
# Error message is logged and transaction is rolled back

# def test_close_with_unresolved_transaction():
#     ds = get_test_db_connection()
#     dao_session = ds.get_dao_session()

#     dao_session.begin()
#     with pytest.raises(Exception, match="unresolved Transaction"):
#         dao_session.close()
#     dao_session.rollback()
#     dao_session.close()

#     ds.disconnect()

def test_close_after_commit():
    ds = get_test_db_connection()
    dao_session = ds.get_dao_session()  

    dao_session.begin()
    dao_session.txn.run("RETURN 1")
    dao_session.commit()
    dao_session.close()

    # if no error raised, close worked
    assert True

    ds.disconnect()

def test_begin_twice_only_one_txn():
    ds = get_test_db_connection()
    dao_session = ds.get_dao_session()

    dao_session.begin()
    
    with pytest.raises(Exception, match="Transaction already open; nested transactions are not supported"):    
        dao_session.begin()  

    dao_session.rollback()
    dao_session.close()

    ds.disconnect()

def test_double_commit():
    ds = get_test_db_connection()
    dao_sess = ds.get_dao_write_session()
    ex_str = None
    try:
        dao_sess.begin()
        dao_sess.commit()
        dao_sess.commit()
    except Exception as e:
        ex_str = str(e)

    assert ex_str is not None

    dao_sess.close()
    ds.disconnect()

def test_double_rollback():
    ds = get_test_db_connection()
    dao_sess = ds.get_dao_write_session()
    ex_str = None
    try:
        dao_sess.begin()
        dao_sess.rollback()
        dao_sess.rollback()
    except Exception as e:
        ex_str = str(e)

    assert ex_str is not None

    dao_sess.close()
    ds.disconnect()

def test_section_session():
    print_msg("Session tests")
    assert True

def test_operation_after_close():
    ds = get_test_db_connection()
    dao_sess = ds.get_dao_write_session()
    dao_sess.close()
    with pytest.raises(Exception, match="NEO4J Session is closed"):
        db_name = dao_sess.query("CALL db.info() YIELD name RETURN name", format="SINGLE")  

    dao_sess = ds.get_dao_write_session()
    dao_sess.close()
    with pytest.raises(Exception, match="NEO4J Session is closed"):
        dao_sess.update("MERGE (t:Test  {id:'1'})")

    ds.update("MATCH (t:Test) detach delete t")
    ds.disconnect()

def test_with_statement():
    ds = get_test_db_connection()

    db_name = ""
    s_ref = None
    try:
        with ds.get_dao_read_session() as s:
            s_ref = s
            db_name = s.query("CALL db.info() YIELD name RETURN name", format="SINGLE")    
    except Exception:
        pass

    assert db_name == CONN_DETAILS["con_database"]
    assert s_ref.get_session().closed()
    assert all(entry["sess"].id != s_ref.id for entry in ds.active_sessions)

    ds.disconnect()

def test_with_statement_transaction():
    ds = get_test_db_connection()
    ds.update("MATCH (t:Test) detach delete t")
    node_count = 0
    s_ref = None
    try:
        with ds.get_dao_write_session() as s:
            s_ref = s
            s.begin()
            s.update("MERGE (t:Test  {id:'1'})")  
            s.commit()  
            node_count = s.query("MATCH (t:Test  {id:'1'}) RETURN count(t) as cnt", format="SINGLE")

    except Exception:
        s.rollback()

    assert node_count == 1
    assert s_ref.get_session().closed()
    assert all(entry["sess"].id != s_ref.id for entry in ds.active_sessions)

    ds.update("MATCH (t:Test) detach delete t")
    ds.disconnect()

def test_with_statement_transaction_context():
    ds = get_test_db_connection()
    ds.update("MATCH (t:Test) detach delete t")
    node_count = 0
    s_ref = None
    try:
        with ds.get_dao_write_session() as s:
            s_ref = s
            with s.transaction():
                s.update("MERGE (t:Test  {id:'1'})")  
            node_count = s.query("MATCH (t:Test  {id:'1'}) RETURN count(t) as cnt", format="SINGLE")

    except Exception:
        s.rollback()

    assert node_count == 1
    assert s_ref.get_session().closed()
    assert all(entry["sess"].id != s_ref.id for entry in ds.active_sessions)

    ds.update("MATCH (t:Test) detach delete t")
    ds.disconnect()

def test_with_session_transaction_exception_handling():
    ds = get_test_db_connection()
    ds.update("MATCH (t:Test) detach delete t")
    node_count = 0
    s_ref = None

    with pytest.raises(Exception, match="Unable to write data to a readonly connection"):
        with ds.get_dao_read_session() as s:
            s_ref = s
            with s.transaction():
                s.update("MERGE (t:Test  {id:'1'})")  
            node_count = s.query("MATCH (t:Test  {id:'1'}) RETURN count(t) as cnt", format="SINGLE")

    assert s_ref.get_session().closed()
    assert all(entry["sess"].id != s_ref.id for entry in ds.active_sessions)

    ds.update("MATCH (t:Test) detach delete t")
    ds.disconnect()    

def test_get_session_returns_session():
    ds = get_test_db_connection()

    dao_session = ds._get_session()
    assert isinstance(dao_session, Session)
    dao_session.close()
    ds.disconnect()

def test_get_dao_session_returns_session():
    ds = get_test_db_connection()

    dao_session = ds.get_dao_session()
    assert isinstance(dao_session, AntarpyNeo4jSession)
    dao_session.close()
    ds.disconnect()


def test_set_impersonated_user_effect():
    ds = AntarpyNeo4jDatasource()
    ds.set_impersonated_user("alice")
    assert ds.impersonatedUser == "alice"

def test_successful_write_no_retry():
    ds = get_test_db_connection()
    policy = AntarpyNeo4jRetryPolicy(retries=3, backoff=0.1)

    def op():
        return ds.update("CREATE (n:RetryTest {value: 'ok'}) RETURN n")

    result = policy.run(op)
    assert len(result) == 1

    # Cleanup
    ds.update("MATCH (n:RetryTest {value: 'ok'}) DELETE n")
    ds.disconnect()


def test_retry_on_session_expired():
    ds = get_test_db_connection()
    policy = AntarpyNeo4jRetryPolicy(retries=2, backoff=0)

    def op():
        raise SessionExpired("fake session expiration")

    with pytest.raises(SessionExpired):
        policy.run(op)

    ds.disconnect()


def test_client_error_not_retried():
    ds = get_test_db_connection()
    policy = AntarpyNeo4jRetryPolicy(retries=3, backoff=0)

    def op():
        return ds.query("INVALID CYPHER SYNTAX")

    with pytest.raises(ClientError):
        policy.run(op)
    
    ds.disconnect()

def test_succeeds_after_initial_failure():
    ds = get_test_db_connection()
    policy = AntarpyNeo4jRetryPolicy(retries=3, backoff=0)

    calls = []

    def op():
        if not calls:
            calls.append("fail")
            raise SessionExpired("fake session expiration")
        return ds.query("RETURN 1 AS val")

    result = policy.run(op)
    assert result[0]["val"] == 1

    ds.disconnect()

def test_connection_access_mode():
    ds = get_test_db_connection()

    dao_session = ds.get_dao_read_session()

    error_msg = ""

    try:
        #ds.update("MERGE (t:TestNode {name: 'JC'})", dao_session=dao_session)
        dao_session.update("MERGE (t:TestNode {name: 'JC'})")
    except Exception as e:
        error_msg = str(e)

    assert error_msg == "Unable to write data to a readonly connection."

    dao_session.close()
    ds.disconnect()

def test_session_register_in_datasource():

    ds = get_test_db_connection()

    dao_session1 = ds.get_dao_read_session()
    dao_session2 = ds.get_dao_write_session()

    assert len(ds.active_sessions) == 2

    dao_session1.close()
    assert len(ds.active_sessions) == 1
    ds.close()
    assert len(ds.active_sessions) == 0

    err_msg = ""
    try:
        dao_session2.run("RETURN 1")
    except Exception:
        err_msg = "Service is Unavailable"
    
    assert err_msg == "Service is Unavailable"


def test_section_stats():
    print_msg("Stats tests")
    assert True

def test_run_stats_generation():
    ds = get_test_db_connection()
    
    dao_session = ds.get_dao_read_session()
    dao_session.set_collect_stats(True)
    
    cypher = "MATCH (n) return count(n)"
    #result = ds.query(cypher, dao_session=dao_session)
    result = dao_session.query(cypher)
    
    run_stats = dao_session.get_query_stats()
    assert run_stats["cypher"] == cypher

    dao_session.close()
    ds.disconnect()

def test_profile_generation():
    ds = get_test_db_connection()
    
    dao_session = ds.get_dao_read_session()
    dao_session.set_profile_cypher(True)
    
    cypher = "MATCH (n) return count(n)"
    #result = ds.query(cypher, dao_session=dao_session)
    result = dao_session.query(cypher)
    
    run_stats = dao_session.get_query_stats()
    assert len(run_stats["profile_plan"]) > 0

    dao_session.close()

    ds.disconnect()

def test_section_database_scenarios():
    print_msg("Database Scenarios tests")
    assert True

def test_concurrent_writes_same_node():

    ds = get_test_db_connection()
    # Clean out any existng data
    ds.update("MATCH (a:Acct) detach delete a")    

    acct_id = 1
    """Ensures a single account node exists with a known balance."""
    ds.update("MERGE (a:Acct {id: $id}) SET a.balance = 0, a.updated = timestamp()", {"id": acct_id})

    def _increment_once(ds, acct_id: int, delta: int, start_barrier: threading.Barrier, done_event: threading.Event, errors: list[str]):
        """
        Worker that opens a WRITE session, begins a tx, and increments the balance.
        The barrier makes both threads attempt the write at the same time to provoke a lock/serialize.
        """
        s = ds.get_dao_write_session()
        try:
            s.begin()
            # Synchronize both transactions right before touching the node.
            start_barrier.wait(timeout=5.0)
            # Update in the same tx to hold the node lock for the critical section.
            s.update("MATCH (a:Acct {id:$id}) SET a.balance = a.balance + $d", {"id": acct_id, "d": delta})
            s.commit()
        except Exception as e:
            # If your DAO’s retry policy fails, we capture the exception for assertions.
            try:
                s.rollback()
            except Exception:
                pass
            errors.append(repr(e))
        finally:
            s.close()
        done_event.set()

    def read_balance(ds, acct_id: int) -> int:
        return ds.query("MATCH (a:Acct {id:$id}) RETURN a.balance AS b", {"id": acct_id},format="SINGLE" )

    """
    Two concurrent write transactions update the SAME node.
    Expected:
      - Neo4j serializes the writes (second waits for lock) OR
      - If your DAO enforces short timeouts, one may retry transparently.
    Pass condition: final balance == sum of deltas and no unhandled errors.
    """
    # sanity
    assert read_balance(ds, acct_id) == 0

    # Prepare two concurrent writers hitting the same node.
    barrier = threading.Barrier(2)
    done1 = threading.Event()
    done2 = threading.Event()
    errors: list[str] = []

    t1 = threading.Thread(target=_increment_once, args=(ds, acct_id, 5, barrier, done1, errors))
    t2 = threading.Thread(target=_increment_once, args=(ds, acct_id, 7, barrier, done2, errors))

    t1.start()
    t2.start()
    done1.wait(10.0)
    done2.wait(10.0)
    t1.join(timeout=1.0)
    t2.join(timeout=1.0)

    # Assert no unhandled exceptions were raised by workers.
    assert not errors, f"Concurrent increment raised errors: {errors}"

    # Final balance should be the sum of both deltas (no lost updates).
    final_balance = read_balance(ds, acct_id)
    assert final_balance == 12, f"Expected balance 12 after concurrent writes, got {final_balance}"

    # cleanup if you want:
    ds.update("MATCH (a:Acct {id:$id}) DETACH DELETE a", {"id": acct_id})
    ds.close()

#Constraint/index violations (non-retriable) Goal: Ensure you don’t retry non-transient errors and that batch paths report per-row failures.
def test_constraint_violation():
    ds = get_test_db_connection()
    # Clean out any existng data
    ds.update("MATCH (a:Row) detach delete a")

    ds.update("CREATE CONSTRAINT row_id IF NOT EXISTS FOR (r:Row) REQUIRE r.id IS UNIQUE")
    alist = [{"id": 100}, {"id": 100}]  # duplicate
    ex_str = None
    try:
        result = ds.update("CREATE (r:Row {id: $id})", alist)
    except Exception as e:
        ex_str = str(e)

    assert ex_str is not None
    
    # Clean out any existng data
    ds.update("MATCH (a:Row) detach delete a")

    ds.close()

def test_write_conflict_timeout_surface_clean_error():
    """
    Force a timeout to ensure clean error surfacing (no infinite waits).
    Strategy:
      - TX1 holds the node 'long' (client sleep).
      - TX2 attempts to write with a tiny server/client timeout configured for the test environment,
        expecting a timeout error (non-retriable).
    """
    # 0) Ensure the row exists so both txs lock the SAME node
    ds = get_test_db_connection()

    # Clean out any existng data
    ds.update("MATCH (a:Acct) detach delete a")

    ds.update("MERGE (a:Acct {id:$id}) SET a.balance = 0", {"id": 1})
    acct_id = 1

    lock_ready = threading.Event()
    err_box = {"err": None}

    def holder_tx():
        s1 = ds.get_dao_write_session()
        s1.begin()
        try:
            # Bypass internals to force a timeout. 
            # This write acquires a write-lock on the node
            s1.txn.run("MATCH (a:Acct {id:$id}) SET a.marker = $t",{"id": acct_id, "t": int(time.time()*1000)})
            lock_ready.set()                       # signal: lock is now held
            time.sleep(2.0)                        # keep the tx open → lock stays held
            s1.commit()

        finally:
            s1.close()

    def writer2():
        s2 = ds.get_dao_write_session()
        try:
            # IMPORTANT: timeout is in **seconds** for begin_transaction
            s2.begin(timeout=0.25)
            s2.update("MATCH (a:Acct {id:$id}) SET a.balance = a.balance + 1", {"id": acct_id})
            s2.commit()
        except Exception as e:
            #print(str(e))
            err_box["err"] = e
            s2.rollback()        
        finally:
            s2.close()

    t1 = threading.Thread(target=holder_tx)
    t1.start()
    lock_ready.wait(2.0)          # wait until TX1 has done the write and holds the lock
    t2 = threading.Thread(target=writer2)
    t2.start()
    t1.join()
    t2.join()

    assert err_box["err"] is not None, "Expected timeout/error when lock was held, but none occurred."

    # Clean out any existng data
    ds.update("MATCH (a:Acct) detach delete a")    
    ds.close()

def test_deadlock():

    ds = get_test_db_connection()
    # Clean out any existng data
    ds.update("MATCH (a:Row) detach delete a")

    # Ensure nodes exist
    ds.update("UNWIND [1,2] AS i MERGE (r:Row {id:i}) SET r.x = 0")

    barrier = threading.Barrier(2)
    outcome = {"A": {"ok": False, "err": None}, "B": {"ok": False, "err": None}}

    def writer(name, first, second):
        s = ds.get_dao_write_session()
        try:
            # IMPORTANT: this must start an explicit tx INSIDE your DAO
            s.begin()

            # Step 1: take the first lock
            s.update("MATCH (r:Row {id:$id}) SET r.x = coalesce(r.x,0)+1", {"id": first})

            # Step 2: wait until the other thread also took its first lock
            barrier.wait(timeout=5.0)

            # Step 3: both try to take the other lock -> deadlock; one thread will be aborted
            s.update("MATCH (r:Row {id:$id}) SET r.x = coalesce(r.x,0)+1", {"id": second})

            s.commit()
            outcome[name]["ok"] = True
        except Exception as e:
            #print(f'Thread Exception {str(e)}')
            outcome[name]["err"] = e
            try:
                s.rollback()
            except Exception:
                pass
        finally:
            s.close()

    tA = threading.Thread(target=writer, args=("A", 1, 2))
    tB = threading.Thread(target=writer, args=("B", 2, 1))
    tA.start(); tB.start()
    tA.join(); tB.join()

    # Exactly one should fail with a transient deadlock, the other should succeed
    errs = [v["err"] for v in outcome.values() if v["err"] is not None]
    oks  = [v["ok"]  for v in outcome.values() if v["ok"]]
    assert len(errs) == 1 and len(oks) == 1, f"Expected one deadlock failure & one success, got: {outcome}"
    msg = str(errs[0])
    #print(f'Exception : {msg}')
    assert ("Deadlock" in msg) or ("TransientError" in msg), f"Unexpected error for deadlock: {msg}"

    # Final state: the successful tx incremented both rows (+1 each); the failed one rolled back
    got = [(row["id"], row["x"]) for row in ds.query("MATCH (r:Row) RETURN r.id AS id, r.x AS x ORDER BY id")]
    assert got == [(1, 1), (2, 1)], f"Unexpected final values: {got}"

    # Clean out any existng data
    ds.update("MATCH (a:Row) detach delete a")

    ds.close()

#Bookmark / causal consistency Goal: Verify save_bookmark + use_bookmark wiring guarantees read-your-writes across sessions.
def test_bookmarks():
    ds = get_test_db_connection()
    ds.update('MATCH (n:Person {name: "Alice"}) detach delete n')

    session_A  = ds.get_dao_write_session(save_bookmark="p_update")  # or ds.get_dao_session(save_bookmark="p_update") if default access mode = WRITE (init_dao)
    session_A1 = ds.get_dao_write_session(save_bookmark="p_update")
    try:
        
        session_A.begin()
        session_A.update('CREATE (n:Person {name: "Alice", surname:"Wong", age:34})')
        session_A.commit()
        
        session_A1.begin()
        session_A1.update('CREATE (n:Person {name: "Alice", surname:"Travis", age:23})')
        session_A1.commit() 

        session_B = ds.get_dao_read_session(use_bookmark="p_update")
        combined_age = session_B.query('MATCH (n:Person) WHERE n.name="Alice" return sum(n.age) as combined_age', format="SINGLE")        
        assert combined_age == 57

        session_B.close()
    except Exception as e:
        try:
            session_A.rollback()
            session_A1.rollback()
        except Exception:
            pass
    finally:
        session_A.close()
        session_A1.close()

    # Make sure pruning worked.
    assert len(ds.bookmarks.get_tags()) == 0

    ds.update('MATCH (n:Person {name: "Alice"}) detach delete n')  
    ds.close()

def test_intentional_lock_wait_timeout():
    ds = get_test_db_connection()
    ds.con_details["num_retry"] = 0  # don't hide the error with retries

    # Clean & seed
    ds.update("MATCH (a:Acct) DETACH DELETE a")
    ds.update("MERGE (a:Acct {id:1}) SET a.balance = 0")

    lock_ready = threading.Event()
    err_box = {"err": None}

    # TX-A: take the lock and keep the tx open
    def holder():
        s = ds.get_dao_write_session()
        try:
            s.begin()  # explicit tx (no timeout)
            s.update("MATCH (a:Acct {id:1}) SET a.marker = $t",
                     {"t": int(time.time()*1000)})
            lock_ready.set()  # signal lock is held
            time.sleep(5.0)   # keep tx open => lock held
            s.commit()
        finally:
            s.close()

    # TX-B: small tx timeout, attempt to write while lock is held
    def writer():
        s = ds.get_dao_write_session()
        try:
            lock_ready.wait(2.0)  # ensure TX-A grabbed the lock
            s.begin(timeout=1.0)  # seconds (driver API uses seconds)
            s.update("MATCH (a:Acct {id:1}) SET a.balance = a.balance + 1")
            s.commit()            # should not reach if timeout occurs
        except Exception as e:
            err_box["err"] = e    # keep the actual exception object
            try: s.rollback()
            except Exception: pass
        finally:
            s.close()

    t1 = threading.Thread(target=holder)
    t2 = threading.Thread(target=writer)
    t1.start(); t2.start()
    t1.join(); t2.join()

    # Expect a timeout-like failure in TX-B
    e = err_box["err"]
    assert e is not None, "Expected a timeout/error while lock was held."
    # Helpful checks: type or code (works across driver versions)
    code = getattr(e, "code", "") or ""
    assert ("TransientError" in code) or ("Timeout" in str(e)) or ("lock" in str(e).lower()), f"Unexpected error: {type(e)} {e}"

    # Cleanup
    ds.update("MATCH (a:Acct) DETACH DELETE a")
    ds.close()


# Timeouts & cancellation Goal: Surface driver timeouts distinctly; no infinite waits.
#Server timeout: Configure a very low dbms.transaction.timeout in a test profile; run a write that blocks (see §1B) → assert timeout class and no retry.
#Client timeout: If you expose a client-side per-query timeout, run a long query CALL apoc.util.sleep(5000) and assert you cancel/timeout cleanly.

#Connection & routing instability Goal: Your retry/connect code should cope with network hiccups.
#Connection drop mid-tx: If you run Neo4j in Docker for tests, start a tx, then docker restart neo4j before commit(); 
# assert you get a retriable connection error on idempotent ops and a clear failure on non-idempotent ones.
#Auth/impersonation: set an invalid impersonated user → assert clear auth error; then a valid one to confirm positive path.


