![Antarpy DAO](https://raw.githubusercontent.com/JeremyChilvers/antarpy_dao/main/AntarPy%20full%20small.png)
<br>

# ANTARPY DAO Neo4j Driver

## Antarpy name origins
Why Antarpy (Antar-pi)? **Antar**esia are non-venomous genus of **py**thon native to Australasia.

## Details - the good oil...
Antarpy DAO Neo4j Driver is a wrapper python library that assists in writing clean accessable Cypher statements

Antarpy DAO Neo4j Driver provides an easy-to-use interface to 
- Create connections to a Neo4j Database instance
    - Define set-and-forget default settings that can be overriden when the need arises
    - Run cypher statements against a different databases easily
    - Run as an Impersonated user
    - Used as a dao_session factory
    - Session and Bookmark automatic cleanup.

- Use Antarpy DAO sessions to 
    - Create Read Only or Read Write connections
    - Bookmark support (supports concurrent bookmarking schemes)
    - Easily get Profile Plan and Query Statistics
    - Simple interface to Transaction Support (Begin, Commit, Rollback)
    - Consistent invocation of cypher across session and datasource (query/update).
    - Obtain access to Neo4j Session for when you want to roll your own!

- Use Antarpy DAO Logging to
    - Log messages to different output types (Console and/or File)
    - Define different logging levels for each output type
    - Pass setting to the log utility through parameters or environment variables.
    - Implement rolling file backup schemes.

- Uses best practises to execute your Cypher statements
    - Datasource allows you to run Cypher statements in virtual sessions (without the overhead of defining transactions. Its all done for you!)
    - Simple query / update method calls
    - Batch update support (Vanilla, apoc.periodic.iterate, Call In Concurrent Transaction)
    - Customisable Retry Policy
    - Transformer support ("LIST","DICT","RECORD","SINGLE","DATAFRAME", "JSON", "CUSTOM")

## How is this different from "neo4j import GraphDatabase"
Antarpy DAO Neo4j Driver was created to simplify database access by 
- providing a single interface to driver operations such as
    - Result Transformers
    - Batch Updates (CICT, APOC, Vanilla)
    - Queries across disparate databases - yet contain a default DB. Only specify DB when required.
    - Defaults Connection information/settings
- providing a consistent interface to driver operations for 
    - Session management
    - Simple operations
    - accessing a neo4j session - if required
- Simplification of transaction management
- Simple interface for Bookmarks across sessions.

And due to out of the box connection pooling, simply create this object in a py file and use everywhere

consider these examples

With Antarpy DAO Driver:
- Default Database is defined on init - dont have to worry about it (unless its different from default)
- "query" method is run as a READ connection always ("update" operation as WRITE)
- this example using out-of-the-box result transformer - format="SINGLE" 
```python
query = (
            "MATCH (p:Person) "
            "WHERE p.name = $person_name "
            "RETURN p.name AS name"
        )
params = { "person_name":person_name}
names = ds.query(query,params,format="SINGLE")
return names
```
instead of the trasitional approach - sure you have ultimate flexibility but at the expense of maintainability
```python
query = (
            "MATCH (p:Person) "
            "WHERE p.name = $person_name "
            "RETURN p.name AS name"
        )
names = self.driver.execute_query(
    query, person_name=person_name,
    database_=self.database, routing_=RoutingControl.READ,
    result_transformer_=lambda r: r.value("name")
)
return names
```
or how about this 

With Antarpy DAO Driver:
- Transactional consistency is baked in and is wrapped in the dao session object.
  No need to build a function for each transaction which reduces code bloat.
- Retry Logic with backoff built in under the covers
- easier to read and more logical

Here are a few ways in which you can use the API
```python
#-----------------------------------------------------------------
# Use WITH syntax for implicit session and transaction management
#-----------------------------------------------------------------
def transfer_to_other_bank(driver, customer_id, other_bank_id, amount):

    try:
        with ds.get_dao_write_session(database="neo4j") as dao_sess
            with dao_sess.transaction() # Implicit begin

                # Multiple updates 
                params = {"id":customer_id, "amount":amount}        
                query = "MATCH (c:Customer {id: $id}) RETURN c.balance >= $amount AS sufficient"
                result = dao_sess.query(query, params, format="SINGLE")
                raise Exception("Operation Failed.")

                other_bank_transfer_api(customer_id, other_bank_id, amount)
                query = "MATCH (c:Customer {id: $id}) SET c.balance = c.balance - $amount"
                result = dao_sess.update(query, params)      
            # Implicit commit

    except Exception as e:
        # Implicit rollback on exceptions
        request_inspection(customer_id, other_bank_id, amount, e)
        raise    
    
    # Implicit session close

```
or this 
```python
#-----------------------------------------------------------------
# Explicitly manage transactions...
#-----------------------------------------------------------------
def transfer_to_other_bank(driver, customer_id, other_bank_id, amount):

    # Create Write Session
    dao_sess = ds.get_dao_write_session(database="neo4j")

    dao_sess.begin()
    try:

        params = {"id":customer_id, "amount":amount}        
        query = "MATCH (c:Customer {id: $id}) RETURN c.balance >= $amount AS sufficient"
        # Query done as a anonymous READ txn - no need for separate function
        result = dao_sess.query(query, params, format="SINGLE")
        raise Exception("Operation Failed.")

        other_bank_transfer_api(customer_id, other_bank_id, amount)
        # Update method uses anonymous WRITE txn - no need for separate function
        query = "MATCH (c:Customer {id: $id}) SET c.balance = c.balance - $amount"
        result = dao_sess.update(query, params)                
        
        dao_sess.commit()
    except Exception as e:
        request_inspection(customer_id, other_bank_id, amount, e)
        dao_sess.rollback()
        raise
    finally:
        dao_sess.close()
    
```

instead of this example from Neo4j

```python
def transfer_to_other_bank(driver, customer_id, other_bank_id, amount):
    with driver.session(
        database="neo4j",
        # optional, defaults to WRITE_ACCESS
        default_access_mode=neo4j.WRITE_ACCESS
    ) as session:
        tx = session.begin_transaction()
        # or just use a `with` context instead of try/finally
        try:
            if not customer_balance_check(tx, customer_id, amount):
                # give up
                return
            other_bank_transfer_api(customer_id, other_bank_id, amount)
            # Now the money has been transferred
            # => we can't retry or rollback anymore
            try:
                decrease_customer_balance(tx, customer_id, amount)
                tx.commit()
            except Exception as e:
                request_inspection(customer_id, other_bank_id, amount, e)
                raise
        finally:
            tx.close()  # rolls back if not yet committed


def customer_balance_check(tx, customer_id, amount):
    query = ("MATCH (c:Customer {id: $id}) "
             "RETURN c.balance >= $amount AS sufficient")
    result = tx.run(query, id=customer_id, amount=amount)
    record = result.single(strict=True)
    return record["sufficient"]
    
def decrease_customer_balance(tx, customer_id, amount):
    query = ("MATCH (c:Customer {id: $id}) "
             "SET c.balance = c.balance - $amount")
    result = tx.run(query, id=customer_id, amount=amount)
    result.consume()    
```
Lets see Antarpy DAO Neo4j Driver in more detail below... 

## Quick Start
### Installing
```python
pip install antarpy-dao
```

### Creating the Datasource object
Define your connection details - from somewhere....and consolidate as a Python Dictionary.
```python
# Your Database details from somewhere i.e. ENV VAR, File etc...
dbUser=os.environ["DBUSERNAME"]
dbPwd=os.environ["DBPASSWORD"]
dbHost=os.environ["DBHOSTNAME"]
dbPort=os.environ["DBPORT"]
dbDb=os.environ["DBDATABASE"]

# Create a Dict
CONN_DETAILS = {
    "con_type": "neo4j",
    "con_hostname": dbHost,
    "con_port": dbPort,
    "con_username": dbUser,
    "con_password": dbPwd,
    "con_database": "neo4j"
}

# Optional settings - These will have defaults if not defined
"""
    CONN_DETAILS["access_mode"]         # Database Access Mode READ/WRITE. Default to "WRITE".
    CONN_DETAILS["num_retry"]           # Number of time to Retry. Default 3. 
    CONN_DETAILS["backoff_multiplier"]  # Increasing amount of time to wait between retries. Default 0.5
    CONN_DETAILS["batch_limit"]         # The default batch size as a hard split when doing batch updates. Will split data list input into "batch_limit" size chunks. Default 10000.
    CONN_DETAILS["trans_size"]          # The default transaction size for a chunk (number of records per transaction). Default 100.

"""
```
Create the Datasource object in a central py file and import ds where required. In built pooling and session manangement will handle the rest.
```python
# central py file....

from antarpy_dao.AntarpyNeo4jDatasource import AntarpyNeo4jDatasource
# Create Datasource object
ds = AntarpyNeo4jDatasource()
# Initialise 
ds.init_dao(CONN_DETAILS)
# Connect
try:
    # Connnect to Database Instance using details passed into init_dao
    ds.connect()

except Exception as e:
    print(str(e))
```
### Closing an instance
```python
ds.close()
```
### Running simple Queries
```python
from <central DAO py file> import ds

try:
    # Transformed as a List of Dicts - Default
    result = ds.query("MATCH (n:TestNode) return count(n) as cnt")
    print(result[0]["cnt"])

    # Transformed as a single unpacked value.
    # NOTE that this DAO does not implement result.single(strict=True)
    #       - for multiple rows returned format="SINGLE" will return the first
    #       - for 'not found' cases the returned value will be None

    cnt = ds.query("MATCH (n:TestNode) return count(n) as cnt", format="SINGLE")
    print(cnt)

    # Transformed as a single unpacked value. Nodes, Paths & Relationships are returned as a DICT.
    result = ds.query("MATCH (t:TestNode {name:'Jeremy'}) return t", format="SINGLE")
    print(result) # {'element_id': '4:d852dfdf-4b61-4c9f-b62a-649c88d9c4f5:76792', 'labels': ['TestNode'], 'properties': {'name': 'Jeremy', 'age': 54, 'height': '182'}}

    # Transformed as JSON - returns data in the following format i.e. 'json': [ data ]
    result = ds.query("MATCH (n:TestNode) return count(n) as cnt", format="JSON")
    print(result)  # {'json' : [{"cnt": 10}]}

    # Custom transformer
    def get_single_person(result):
        record = result.single(strict=True)
        summary = result.consume()
        return record, summary
    
    query = "MERGE (a:Person {name: $name}) RETURN a.name AS name"
    params= {"name":Alice}
    record = ds.update(query,params,format="CUSTOM",result_xform=get_single_person)
    

    # Parameters
    params = {"name": "jeremy", "age": 54}
    # Return as LIST of DICT by default
    result = ds.query("MATCH (n:TestNode) where n.name = $name and n.age = $age return n", params)
    print(result[0]["name"])

    # Processing multiple returned rows
    result = ds.query("MATCH (n:TestNode) return n")
    for rec in result:
        print(rec["name"])

except Exception as e :
    print(str(e))

```
### Running Simple Updates
```python
# Assume datasource "ds" connected
try:
    # basic update
    ds.update("MATCH (n:TestNode) detach delete n")

    # Parameterised
    params = {"name": "jeremy", "age": 54}
    ds.update("MERGE (n:TestNode {name: $name, age: $age})",params)

except Exception as e :
    print(str(e))    
```

### Batch Updates
The following List will be used in all Batch Update Examples i.e. "Standard", "CICT" & "APOC - apoc.periodic.iterate"

```python
alist = [
    {"name":"John",  "age":54},
    {"name":"Peter", "age":24},
    {"name":"Paul", "age":21},
]
```
Note that excessively large input "data lists" will be broken up into "batch_limit" size chunks and will then be processed in a serial manner (according to parallel and trans_size rules)

### Running Standard Batch Updates
Recommended for small lists of < 1000 records

The batch update will in "trans_size" chunks. Any data returned will be collated and passed

```python
cypher_qry = "MERGE (t:TestNode {name: $name}) SET t.age = $age"
# Assume datasource "ds" connected
try: 
    ds.update(cypher_qry, params=alist)
except Exception as e :
    print(str(e))  
```
or when you want to return something
```python
cypher_qry = "MERGE (t:TestNode {name: $name}) SET t.age = $age RETURN t.name as name"
# Assume datasource "ds" connected
try: 
    result = ds.update(cypher_qry, params=alist)
except Exception as e :
    print(str(e))  
```
### Running Call In Concurrent Transaction (CICT) Updates 
CICT Updates were introduced by Neo4j to provide better support for batch updates and superceed APOC Batch Updates, thus this is the preferred method for high performance batch updates.

<div style='font-family: "Fira Code", "Consolas", "Monaco", "Courier New", monospace;'>def batch_update_CICT(self, cypher_str,data_list = None,database = None,trans_size = None,parallel = True,threads = None,on_error = None,retry_sec = 2.5) -> List:<br><br>- cypher_str: Cypher Statement<br>- data_list: A List of Dicts representing data to be updated.<br>- trans_size: The transaction commit count. The number of rows applied between commits<br>- parallel: Whether parallelize the query.<br>- threads: The number of threads to apply. Can be left empty to assume the system defaults.<br>- on_error: What to do in error event. CONTINUE, BREAK, FAIL, RETRY<br>- retry_sec: Number of seconds between retries. Where on_error = RETRY. <br><br></div>⚠️Note: "result" is only returned when on_error is CONTINUE or BREAK.<br>⚠️Note that Neo4j failure handling for on_error='CONTINUE' is that that entire <b>TRANSACTION BATCH</b> fails, and failures are not isolated to the records that have issues....<br>
<br>

```python
try:
    cypher_qry = "MERGE (t:TestNode {name: $name}) SET t.age = $age"

    # Simple update. Batched in default trans_size commits.
    result = ds.batch_update_CICT(cypher_qry, data_list=alist)

    # More Control. Neo4j will determine num threads. Batched in default trans_size commits.
    result1 = ds.batch_update_CICT(cypher_qry, data_list=alist, parallel=True, on_error="CONTINUE")

    # Thread and trans size control
    result2 = ds.batch_update_CICT(cypher_qry, data_list=alist, parallel=True, thread=5, trans_size=2000, on_error="CONTINUE")
except Exception as e:
    print(str(e))    
```


### Running APOC Batch Updates (apoc.periodic.update)
APOC batch updates were introduced to fill a batch update process hole in the early days of Neo4j. This process provides for the ability to parallelize and segment a batch update operation providing speed and stability.

The syntax of a APOC Batch update is defined in the following logical parts (parameters to apoc function)
- data list navigation (optional)
- Match statement
- Operation 
- Operation parameters / settings / options

such as 
```python
CALL apoc.periodic.iterate(
    "UNWIND $myList AS row RETURN row",         # 1. Data List Navigation
    "MATCH (t:TestNode {id:row.id}) RETURN t",  # 2. Match Statement
    "DETACH DELETE t",                          # 3. Operation
    {batchSize: 10, parallel: false}            # 4. Settings
)
```

The Antarpy APOC wrapper method provides an intuitive interface so that you can control each of these sections. 
<br><div style='font-family: "Fira Code", "Consolas", "Monaco", "Courier New", monospace;'>def batch_update_APOC(self, cypher_str, database = None, data_list = None, trans_size = None, parallel = False, apoc_data_list_name = "dataList") -> List:<br><br>- cypher_str: Cypher Statement<br>- database: Allows you to run this against a database different from the defaults (init_dao)<br>- data_list: A List of Dicts representing data to be updated.<br>- trans_size: The transaction commit count. The number of rows applied between commits. If None the defaults to <i>initialisation</i> trans_size <br>- parallel: Whether parallelize the query. Number of Threads managed by apoc routine.<br>- apoc_data_list_name: Name of datalist where you are rolling your own query.</div><br>⚠️Note: A list of dicts of statistics returned.

As such when a cypher statement is passed into the method, it must be passed as 2. Match and 3. Operation embedded strings 

Consider the examples below


```python

try:
    cypher_qry = """ "MERGE (t:TestNode {id: row.name}) SET t.age = row.age" """
    ds = get_test_db_connection()    
    result = ds.batch_update_APOC(cypher_qry, data_list=alist)

    # Simple delete - Note the 2. Match and 3. Operation embedded strings (note trailing comma)
    result2 = ds.batch_update_APOC(""" "MATCH (t:TestNode) RETURN t","DETACH DELETE t", """, trans_size=5)

    # The method can also handle rolling your own. This is valid
    cypher_qry = """
        CALL apoc.periodic.iterate(
            "MATCH (t:TestNode) RETURN t",
            "DETACH DELETE t",
            {batchSize: 10, parallel: false})
            """
    result3 = ds.batch_update_APOC(cypher_qry)

    # This user defined statement is also valid. Note that, as the datalist is predefined in the cypher, we need to denote it as such using the apoc_data_list_name parameter
    cypher_qry = """
        CALL apoc.periodic.iterate(
            "UNWIND $myList AS row RETURN row", 
            "MERGE (t:TestNode {id: row.name})
                SET t.age = row.age",
            {params: {myList: $myList}, batchSize: 10, parallel: false}
        )
    """
    result = ds.batch_update_APOC(cypher_qry, data_list=alist, apoc_data_list_name="myList")

except Exception as e:
    print(str(e))
```
### Sessions
This is where Antarpy DAO Neo4j Driver really shines!

Sessions can be used like the Datasource in that there is no need to micro-manage transactions or create a function for each operation. Simply run a operation from the Antarpy DAO Session Object and all transactional best practices are provided out of the box.

As such, Antarpy DAO Sessions allow you to perform operations with minimal code overhead and are created via the AntarpyNeo4jDatasource object through one of the following methods

<div style='font-family: "Fira Code", "Consolas", "Monaco", "Courier New", monospace;'>
def get_dao_read_session(self, database=None, save_bookmark = None, use_bookmark = None):<br>
def get_dao_write_session(self, database=None, save_bookmark = None, use_bookmark = None):</div>

- database:       If not defined, then default from init_dao
- save_bookmark:  Tag sessions to  be included in bookmark logic
- use_bookmark:   Tag indicating which sessions bookmarks are to be obtained from and collated. 

<i>more on bookmarks below</i>

Or
<div style='font-family: "Fira Code", "Consolas", "Monaco", "Courier New", monospace;'>
def get_dao_session(self, database=None, access_mode=None, save_bookmark = None, use_bookmark = None):</div>

- access_mode:   READ/WRITE - Override for Default access mode as defined in init_dao

⚠️ Query / update operations on the Datasource are also available via the Session object with the notable exclusion of the database parameter as this is defined at session creation time i.e. dao_sess = ds.get_dao_session(database="yourdb")
- query
- update

Batch updates (APOC, CICT) use thier own internal sessions and therefore are called directly from the Datasource class.

Antarpy Sessions come with a **Transaction Context Manager**, which means that begin, commit and rollback logic are provided out of the box

WITH statement can be used with Antarpy sessions, featuring auto close.

⚠️ Note:
- Nested Transactions are not allowed.
- Open Transactions on a session close are rolled back with log message & stack trace 

```python

try:
    with ds.get_dao_write_session(database="test01") as dao_sess:   
        cnt = dao_sess.query("MATCH (n:TestNode) return count(n) as cnt", format="SINGLE")    
        if cnt > 0:

            with dao_sess.transaction(): # auto begin  -  Pass in timeout, metadata into transaction() if required
                dao_sess.update("MATCH (n:TestNode) detach delete n")                 
            # auto commit/rollback - exception raised

        cnt = dao_sess.query("MATCH (n:TestNode) return count(n) as cnt", format="SINGLE")
        print(cnt)
    # Session is auto closed here
except Exception as e:
    print(str(e))   

```

Otherwise you can also do the following

```python

# Note: Access Mode and Database are set as per init_dao. 
# In this example we want to access a different database
dao_sess = ds.get_dao_session(database="test01") 
dao_sess.begin()  # Pass in timeout, metadata into begin() if required

try:   
    cnt = dao_sess.query("MATCH (n:TestNode) return count(n) as cnt", format="SINGLE")

    if cnt > 0:
        dao_sess.update("MATCH (n:TestNode) detach delete n")

    result = dao_sess.query("MATCH (n:TestNode) return count(n) as cnt")
    print(result[0]["cnt"])

    dao_sess.commit()

except Exception as e :
    dao_sess.rollback()
    print(str(e))   
finally:
    # Always remember to close your sessions
    dao_sess.close()
```
## Bookmarks

Neo4j bookmarks provide a way to ensure causal consistency across multiple sessions by passing a transaction commit point from one session to another. When a bookmark is given to a new session, Neo4j ensures that the queries in that session will only run once the database has processed at least that commit point. This is particularly important in clustered environments, where bookmarks help ensure that reads reflect prior writes, even when the sessions are routed to different cluster members.

```pgsql
[ Session A ] (Write)                 [ Session B ] (Read)
---------------------------           ---------------------------
1. Begin TX on Leader
2. CREATE (n:Person {name: "Alice"})
3. Commit TX
   |
   | Commit generates Bookmark: "BM1"
   v
4. Bookmark "BM1" returned
                                     5. Session B starts
                                     6. Pass bookmark ["BM1"] to Session B
                                     7. Driver requests a node that has processed "BM1"
                                     8. If follower not yet at BM1 → wait / choose another node
                                     9. MATCH (n:Person) WHERE n.name="Alice"
                                     10. Return result → guaranteed to include Alice
```

Bookmarks can be implemented in the Antarpy Neoj Datasource when creating a session

<div style='font-family: "Fira Code", "Consolas", "Monaco", "Courier New", monospace;'>
def get_dao_read_session(self, database=None, save_bookmark = None, use_bookmark = None):<br>
def get_dao_write_session(self, database=None, save_bookmark = None, use_bookmark = None):</div>

<br>

- save_bookmark:  Tag sessions to  be included in bookmark logic<br>
- use_bookmark:   Tag indicating which sessions bookmarks are to be obtained from and collated. 

<br>

Antarpy DAO Bookmark Manager (which is part of AntarpyNeo4jDatasource) automatically stores the latest bookmark for a session and "bookmark tag" via the save_session parameter. The Bookmark manager is automatically updated with the latest bookmark whenever a session **commit** occurs.

When a "use_bookmark" operation is invoked for a "bookmark tag", all save_session bookmarks are collated and returned to be included in the  "use_bookmark" session creation operation.

This reduces bookmark management to a simple mechanism of tagging associated sessions as they are created (with a save or use directive). Additionally, multiple different bookmark schemes can be created for a datasource using the "bookmark tag" as the key.

As sessions are closed and cleared, the datasource object will prune the bookmark manager of obselete bookmark entries.

```python

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
    print(f'Combined Age is: {combined_age}')

    session_B.close()

except Exception as e:
    session_A.rollback()
    session_A1.rollback()

finally:
    # Close sessions after 
    session_A.close()
    session_A1.close()


```
```pgsql
Session A (WRITE) → Commit → Bookmark "BM1"
                          ↘
                          Session A1 (WRITE) → Commit → Bookmark "BM2"
                                                    ↘
                                                        Session B (READ, bookmark="BM1" + "BM2") → Wait or route → Guaranteed fresh data
```
# Obtaining a Neo4j Session

In those situations where you need to manage sessions directly, you can obtain a **proper** Neo4j Session through the Antarpy Session object

```python

dao_sess = ds.get_dao_write_session()

neo4j_session = dao_sess.get_session()

```
# Query Statistics

Antarpy DAO Sessions provide the ability to capture 
- Summary info (Statistics)
- Profile info
through the following methods

```python
dao_sess = ds.get_dao_write_session()
dao_sess.set_collect_stats(True)
dao_sess.set_profile_cypher(True)

result = dao_sess.query("MATCH (t:Thread)-[]->(m:Message) return t,m", database="config")
stats = dao_sess.get_query_stats()

print(f"CYPHER:{stats['cypher']} \nPARAMETERS:{stats['parameters']} \nSUMMARY:{stats['summary']}")
print("PROFILE:")
print(stats['profile_plan'])

dao_sess.close()
ds.close()
```
Where the return from dao_sess.get_query_stats() is a dict 
```python
{
    "cypher":"",
    "parameters":{},
    "summary":{},
    "profile":""
}
```
yielding the following output
```sh
CYPHER:PROFILE MATCH (t:Thread)-[]->(m:Message) return t,m
PARAMETERS:None
SUMMARY:{'result_available_after_ms': 1, 'result_consumed_after_ms': 3, 'contains_updates': False, 'nodes_created': 0, 'nodes_deleted': 0, 'relationships_created': 0, 'relationships_deleted': 0, 'properties_set': 0, 'labels_added': 0, 'labels_removed': 0, 'indexes_added': 0, 'indexes_removed': 0, 'constraints_added': 0, 'constraints_removed': 0, 'system_updates': 0, 'contains_system_updates': False}
PROFILE:
+------------------+----+-------------------+----------------+------+---------+----------------+------------------------+-----------+---------------------+
| Operator         | Id | Details           | Estimated Rows | Rows | DB Hits | Memory (Bytes) | Page Cache Hits/Misses | Time (ms) | Pipeline            |
+------------------+----+-------------------+----------------+------+---------+----------------+------------------------+-----------+---------------------+
| +ProduceResults  |  0 | t, m              |              8 |    8 |     135 |              0 |                        |           |                     |
| |                +----+-------------------+----------------+------+---------+----------------+                        |           |                     |
| +Filter          |  1 | t:Thread          |              8 |    8 |      16 |                |                        |           |                     |
| |                +----+-------------------+----------------+------+---------+----------------+                        |           |                     |
| +Expand(All)     |  2 | (m)<-[anon_0]-(t) |              8 |    8 |      16 |                |                        |           |                     |
| |                +----+-------------------+----------------+------+---------+----------------+                        |           |                     |
| +NodeByLabelScan |  3 | m:Message         |             10 |    8 |       9 |            248 |                   65/0 |     2.565 | Fused in Pipeline 0 |
+------------------+----+-------------------+----------------+------+---------+----------------+------------------------+-----------+---------------------+

```

Statistics can also be toggled by using the following environment variable. Handy to profile queries in prod without code changes.

Your .env script.
```shell
# This variable will generate both Summary and Profile stats
export ANTARPYDAO_STATS="TRUE"
```
In this case stats will be logged using logger.info()

# Logging

Logging for AntarpyNeo4jDatasource and AntarpyNeo4jSession both set logging to logging.NullHandler() as standard so you can implement your own logging scheme.

Alternatively you can use the AntarpyLogging configuration tool as follows
```python
from antarpy_dao.AntarpyLogging import setup_antarpy_logging

"""
def setup_antarpy_logging(
    logger_name: str = "antarpy_dao",
    *,
    # If any of these are None, they’ll be pulled from env vars
    overall_level: str | None = None,       # ANTARPYDAOLOG_LEVEL
    console_level: str | None = None,       # ANTARPYDAOLOG_CONSOLE_LEVEL
    file_level: str | None = None,          # ANTARPYDAOLOG_FILE_LEVEL
    file_path: str | None = None,           # ANTARPYDAOLOG_FILE_PATH
    use_console: bool | None = None,        # ANTARPYDAOLOG_CONSOLE=true/false
    use_file: bool | None = None,           # ANTARPYDAOLOG_FILE=true/false
    fmt: str | None = None,                 # ANTARPYDAOLOG_FORMAT
    datefmt: str | None = None,             # ANTARPYDAOLOG_DATEFMT
    propagate: bool | None = None,          # ANTARPYDAOLOG_PROPAGATE=true/false
    rotating: bool | None = None,           # ANTARPYDAOLOG_ROTATING=true/false
    max_bytes: int | None = None,           # ANTARPYDAOLOG_MAX_BYTES
    backup_count: int | None = None,        # ANTARPYDAOLOG_BACKUP_COUNT
):
"""

setup_antarpy_logging()  # defaults: console=INFO, no file, overall=INFO
```
Console INFO + File DEBUG
```python
os.environ["ANTARPYDAOLOG_FILE"] = "true"
os.environ["ANTARPYDAOLOG_FILE_PATH"] = "antarpy.log"
os.environ["ANTARPYDAOLOG_CONSOLE_LEVEL"] = "INFO"
os.environ["ANTARPYDAOLOG_FILE_LEVEL"] = "DEBUG"
setup_antarpy_logging()
```
Rotating file (10 MB - default, 5 backups - default) + quiet console:
```python
os.environ.update({
    "ANTARPYDAOLOG_FILE": "true",
    "ANTARPYDAOLOG_FILE_PATH": "antarpy.log",
    "ANTARPYDAOLOG_ROTATING": "true",
    "ANTARPYDAOLOG_CONSOLE_LEVEL": "WARNING",
})
setup_antarpy_logging(overall_level="DEBUG")
```
# Antarpy DAO API

##  DAO Datasource Class (AntarpyNeo4jDatasource)

The following table shows a list of methods that you can call for the Antarpy Datasource class

| Method         | Short Description |
| --------      | ------- |
| init_dao       | Initialize the Datasource object with the Dict of parameters. Settings include<br><br>- con_type: Type of connection i.e. bolt, neo4j etc<br>- con_hostname: Hostname / IP Address of the Database Engine<br>- con_port: Database Engine Port<br>- con_username: User name to connect to the Database Engine<br>- con_password: Password to connect to the Database Engine<br>- con_database: Default database used for session connects<br><br>Optional Settings<br>- access_mode:  Database Access Mode READ/WRITE. Default to "WRITE".<br>- num_retry: Number of time to Retry. Default 3. <br>- backoff_multiplier: Increasing amount of time to wait between retries. Default 0.5<br>- batch_limit: The default list size when doing batch updates. Will split data list input into "batch_limit" size chunks. Default 10000.<br>- trans_size: The default transaction size for a chunk (number of records per transaction). Default 100. |
| connect       | Connect to a Neo4j Database Instance      |
| disconnect    | Disconnect from a Neo4j Database Instance    |
| close         | Same a disconnect - convenience method | 
| query         |The query method in the Antarpy Neo4j Datasource class allows you to write queries with maximum flexibility and minimum overhead<br>The Datasource class will define its own READ ONLY session and will run the query in a generic "explicit transaction function"<br><br><div style='font-family: "Fira Code", "Consolas", "Monaco", "Courier New", monospace;'>    def query(self, cypher_str, params=None,  database=None, format="DICT", result_xform = None):<br><br>       - cypher_str: Cypher Statement<br>- params: Dict of parameters<br>- database: Run this query against another database<br>- format: Result Transformer. Values include "LIST","DICT","RECORD","SINGLE","DATAFRAME", "JSON", "CUSTOM"<br>- result_xform: Custom Result Transformer function. Used where format="CUSTOM"</div>|
| update        | The update method allows you to perform changes in the database in an annonymous WRITE session.<br><br><div style='font-family: "Fira Code", "Consolas", "Monaco", "Courier New", monospace;'>def update(self,cypher_str, params=None, database=None, format="DICT",result_xform = None, trans_size = None): <br><br> - cypher_str: Cypher Statement<br> - params - a DICT or a LIST[DICT] of parameters to be used in the query<br> - database: Allows you to run this against a database different from the defaults (init_dao)<br> - format: Result Transformer. Values include "LIST","DICT","RECORD","SINGLE","DATAFRAME", "JSON", "CUSTOM"<br>- result_xform: Custom Result Transformer function. Used where format="CUSTOM"<br>- trans_size: The transaction commit count. The number of rows applied between commits </div>|
| batch_update_APOC | Allows the ability to run <i>apoc.periodic.update</i> batch updates.<br><br><div style='font-family: "Fira Code", "Consolas", "Monaco", "Courier New", monospace;'>def batch_update_APOC(self, cypher_str, database = None, data_list = None, trans_size = None, parallel = False, apoc_data_list_name = "dataList") -> List:<br><br>- cypher_str: Cypher Statement<br>- database: Allows you to run this against a database different from the defaults (init_dao)<br>- data_list: A List of Dicts representing data to be updated.<br>- trans_size: The transaction commit count. The number of rows applied between commits<br>- parallel: Whether parallelize the query. Number of Threads managed by apoc routine.<br>- apoc_data_list_name: Name of datalist where you are rolling your own query.</div><br><br>⚠️Note: A list of dicts of statistics returned.|
| batch_update_CICT | Allows the ability to run "Call in Concurrent Transaction" updates.<br><br><div style='font-family: "Fira Code", "Consolas", "Monaco", "Courier New", monospace;'>def batch_update_CICT(self, cypher_str,data_list = None,database = None,trans_size = None,parallel = True,threads = None,on_error = None,retry_sec = 2.5) -> List:<br><br>- cypher_str: Cypher Statement<br>- data_list: A List of Dicts representing data to be updated.<br>- trans_size: The transaction commit count. The number of rows applied between commits<br>- parallel: Whether parallelize the query.<br>- threads: The number of threads to apply. Can be left empty to assume the system defaults.<br>- on_error: What to do in error event. CONTINUE, BREAK, FAIL, RETRY<br>- retry_sec: Number of seconds between retries. Where on_error = RETRY. <br><br></div>⚠️Note: Status list returned when on_error is CONTINUE or BREAK. |
| is_connected  | Allows you to see whether the datasource is connected to an instance |
| set_impersonated_user | Allows the ability to impersonate another user |
| get_dao_session | Creates a DAO Session object.<br><br>  <div style='font-family: "Fira Code", "Consolas", "Monaco", "Courier New", monospace;'> def get_dao_session(self, database=None, access_mode=None, save_bookmark = None, use_bookmark = None):<br>- access_mode:   Override for Default access mode as defined in init_dao<br>- database:       If not defined, then default from init_dao<br>- save_bookmark:  Tag for session to be included in bookmark logic<br>- use_bookmark:   Tag for session to read current bookmarks from save_bookmark sessions</div> |
| get_dao_read_session | Creates a READ ONLY DAO Session object.<br><br>  <div style='font-family: "Fira Code", "Consolas", "Monaco", "Courier New", monospace;'>def get_dao_read_session(self, database=None, save_bookmark = None, use_bookmark = None):<br>- database:       If not defined, then default from init_dao<br>- save_bookmark:  Tag for session to be included in bookmark logic<br>- use_bookmark:   Tag for session to read current bookmarks from save_bookmark sessions</div>|
| get_dao_write_session |  Creates a WRITE DAO Session object<br><br> <div style='font-family: "Fira Code", "Consolas", "Monaco", "Courier New", monospace;'>def get_dao_read_session(self, database=None, save_bookmark = None, use_bookmark = None):<br>- database:       If not defined, then default from init_dao<br>- save_bookmark:  Tag for session to be included in bookmark logic<br>- use_bookmark:   Tag for session to read current bookmarks from save_bookmark sessions</div>| 


##  DAO Session Class (AntarpyNeo4jSession)
| Method         | Short Description |
| --------      | ------- |
| begin          | Start a transaction. NEO4j arguments are passed through i.e. timeout options. |
| commit         | Commit a transaction |
| rollback       | Rollback a transaction |
| close          | Close a session. |
| transaction    | Allows you to use the WITH syntax to create a managed transaction context |
| set_profile_cypher | Determines whether to capture cypher profile data <br><br>def set_profile_cypher(self, status:bool): |
| set_collect_stats | Determine whether to capture cypher run statement statistics<br><br>def set_collect_stats(self, status:bool): | 
| get_query_stats | Gets cypher query statistics based on profile and collect stats flags. | 
| query         | see DAO Datasource Class (AntarpyNeo4jDatasource) - all params except database, which is defined when session is created (explicitly or implicitly via defaults)|
| update        | see DAO Datasource Class (AntarpyNeo4jDatasource) - all params except database, which is defined when session is created (explicitly or implicitly via defaults)|
| get_session | Get a handle to the proper Neo4j session object |
