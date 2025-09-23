Markdown

# SKF Observer

A robust and easy-to-use Python client library designed to simplify integration with the SKF Observer API. This library handles authentication, token refreshing, and provides intuitive methods for reading data and interacting with your Observer application programmatically.

## Features

-   **Seamless Authentication:** Automatic handling of access and refresh tokens.
-   **Easy Data Access:** Simple Python functions to retrieve machine data, events, and other Observer resources.
-   **Error Handling:** Built-in error handling for common API responses.
-   **Structured Interface:** A clear, object-oriented approach to API interaction.
-   **Trend Data Managment:**  An easy trend data colleciton compatible with pipelines and data streaming.


## Installation

You can install `skfobserver` using pip:

```python
pip install skfobserver
```
To Upgrade the package, use this `command`:
```python
pip install --upgrade skfobserver
```
 
 

# Summary of the SKF Observer Package and Its Benefits

The SKF Observer Python package is being developed as a more user-friendly and efficient way to interact with the SKF Observer API. Instead of making multiple, complex API calls, the package aims to encapsulate a series of functions into a single client object. This approach simplifies data retrieval and management, making it easier and quicker for developers to use.

---

## Overall Benefits

### **Reduced Complexity**
The package simplifies API interactions by condensing multiple API calls into single, straightforward commands. For example, getting the observer settings with the package takes only one execution, compared to the multiple steps required with the Swagger page, which include obtaining a token and then making another call for the settings.

### One command Create a client and Collect Metadata
```python
import skfobserver 
# option 1: 
try:  
    client = skfobserver.APIClient(username="myuserName",password="myPassword",base_url="http://aaa:111")
try: 
except Exception as e:
    print(str(e))
```

```python
# option 2: 
try:  
    # myConnection2 is a file saved in the user file 
    client = skfobserver.APIClient(profile_name="myConnection2")
try: 
except Exception as e:
    print(str(e))

```
If the credentials were correct, the result is as follows:
```text
Credentials loaded from section 'profile skfobserver' in '..\.skfobserver\.config'.
SKFObserver: Successfully authenticated and obtained tokens. 2025-09-02 13:26:35.475706
APIClient initialized at 'http://aaa:111'
http://aaa:111/v1/settings
http://aaa:111/v1/hierarchy
http://aaa:111/v1/machines
```

The system has successfully created an API client and loaded credentials. It automatically authenticated, saved the access token, and configured it for renewal.

Refrence source page: 
```python
print(client.swagger_page) 
```
The process then automatically collected metadata from the API's endpoints. It has already performed initial statistical analysis on this data, counting the number of assets and identifying their data types.

### **Improved Security**
The package offers a more secure method for handling credentials by allowing users to store sensitive information like usernames and passwords in a local configuration file on their machine rather than in plain text within the code itself. This prevents credentials from being accidentally shared if the Python code file is distributed.

.config file is located in the user folder name ".skfobserver". Below example: 
```text
[profile myConnection1]
username = connectionUser1
password = connectionPass1
base_url = http://aaa:111


[profile myConnection2] 
username = connectionUser2
password = connectionPass2
base_url = http://bbb:222


[profile myConnection3]
username = connectionUser3
password = connectionPass3
base_url = http://ccc:333


```
  

### **Enhanced User Experience (auto tokens renew)**
It handles common, frustrating tasks automatically, such as refreshing access tokens before they expire. Users don't need to manually manage token expiry or re-authenticate. The package is designed to be developer-friendly, offering different syntax options for commands to suit a user's comfort level.<br>

***To simulate the expiry time:*** *We force the _token_expiry_time to a current value :*

```python
from datetime import datetime, timedelta
client._token_expiry_time = datetime.now() + timedelta(seconds=15)
print("new client time is going to expire: ",client._token_expiry_time)
```

```text
new client time is going to expire:  
2025-08-28 16:38:15.238136
```

### **Abstraction and Efficiency**
It abstracts the underlying complexities of the API. Once a client is established, the user can perform various functions like counting nodes, describing the hierarchy, and retrieving specific machine information with minimal effort. It also provides features to dynamically list available node types, so users don't have to rely on static documentation.<br>
<br>**The following are examples functions of code for counting nodes:**<br>
<br>*Once you have the clinet up and ready, 
and you already have some information collected. To make it easy, 
the hirarachy is already built in. Once you have made the authintication call, you have the heirarachy.*

To get quick statistics about the heiearachy 

```python
print(client.hierarchy.describe_counts)
```

```text
[{'nodetype': 'machine', 'count': 135},
 {'nodetype': 'submachine', 'count': 552},
 {'nodetype': 'Derived speed', 'count': 60},
 {'nodetype': 'Derived point', 'count': 6},
 {'nodetype': 'Online dynamic vibration', 'count': 2212},
 {'nodetype': 'Online process', 'count': 12},
 {'nodetype': 'Online speed', 'count': 45},
 {'nodetype': 'Online derived point', 'count': 51}]

```

To get a fresh image of the hierarchy, 
```python
print(hierarchy = client.get_hierarchy())
```
The hierarchy has the following properties that can give quick idea about the system: 
```python
print( hierarchy.hierarchy_name) # property 
print( hierarchy.describe_counts) # property 
print( hierarchy.rootId) # property 

```


To get the hierarachy root name and info

```python
print(client.hierarchy.hierarchy_root)
```

```text
[{'root name': 'my Root', 'root id': 1, 'root parent': 0}]
```

To get total count of all notes, points ...etc in the hierarchy
```python
print(type(client.hierarchy))
"the total count: ",client.hierarchy.count_nodes()
```
```text
all nodes , all status  3112
```

There are multiple ways to execute a command. Here are some variations for the "all nodes, all status" execution. 
*To get an overall status for all node counts, active and inactive.*<br>
```python
hierarchy.count_nodes(node_type = None, is_active =  None)
hierarchy.count_nodes()
hierarchy.count_nodes('all',None)
hierarchy.count_nodes(None,None)

# "all nodes , all Active "
hierarchy.count_nodes('all',True)

# "all nodes , all Inacive "
hierarchy.count_nodes('all',False)
hierarchy.count_nodes(is_active = False) # assumes node_type = 'None' 
```

Or it can be specified to specific type, below example for submachines: 
```python 
print("all submachine , all status ", hierarchy.count_nodes('submachine')) 
print("all submachine , all status ", hierarchy.count_nodes('submachine',None))
print("all submachine , all Active ", hierarchy.count_nodes('submachine',True))
print("all submachine , all Inacive ", hierarchy.count_nodes('submachine',False)) 

```

For IMx Nodes: 
```python  
print("all imx1 , all Active ", hierarchy.count_nodes('imx1',True))
print("all imx1 , all Inacive ", hierarchy.count_nodes('imx1',False))  
```

For points Nodes: 
```python 
print("all points , all status ", hierarchy.count_nodes('point')) 
print("all points , all status ", hierarchy.count_nodes('point',None))
print("all points , all Active ", hierarchy.count_nodes('point',True))
```

For Online Dynamic Vibration Points: 
```python 
print("all Online dynamic vibration , all status ", hierarchy.count_nodes('Online dynamic vibration',None))
print("all Online dynamic vibration , all Active ", hierarchy.count_nodes('Online dynamic vibration',True))
print("all Online dynamic vibration , all Inacive ", hierarchy.count_nodes('Online dynamic vibration',False)) 
```

To list all aviable options to search for and count: 
```python
print()
print("list all available node types to search for")
hierarchy.nodetypes

```

```test
{1: 'machine',
 2: 'submachine',
 3: 'imx1',
 6: 'measurment group',
 10001: 'Derived speed',
 10002: 'Derived point',
 10005: 'Derived process',
 10201: 'Online dynamic vibration',
 10203: 'Online harmonic vibration',
 10206: 'Online process',
 10207: 'Onli .....
 ....
 ...

```


A slice of the hierarchy can be colected by the following command: 
```python
hierarchy_List = hierarchy.to_list(idNode)
hierarchyDf = pd.DataFrame(hierarchy_List)
print(hierarchyDf.head()) 
```

Then it can be converted to a dict():
```python
sliced_hierarchyD = sliced_hierarchy.to_dict()
```

or it can be converted to a list: 
```python
print(sliced_hierarchy.to_list())
hierarchyDf = pd.DataFrame(sliced_hierarchy.to_list())
print(hierarchyDf.head())
```


#### Go up to the top: 
For a node, if you would like to know its parent, and its parent and so on all the way to the top use the function get_parent_chain: 
```python
# new addtinal function 
parent_chain = client.hierarchy.get_parent_chain(node_id = NodeID)
```
The result below shows a step by step going up towards the top of the tree: 
```text
[{'id': 20441,
  'name': 'Constant speed 300 RPM',
  'active': True,
  'parent': 20436,
  'description': '',
  'path': 'Root Folder\\PMP BRGS\\0845102\\0845102 1H DRY 41/06\\Constant speed 300 RPM'},
 {'id': 20436,
  'name': '0845102 1H DRY 41/06',
  'active': True,
  'parent': 20428,
  'description': 'PUMP INBOARD BEARING',
  'path': 'Root Folder\\PMP BRGS\\0845102\\0845102 1H DRY 41/06'},
 {'id': 20428,
  'name': '0845102',
  'active': True,
  'parent': 20397,
  'description': '',
  'path': 'Root Folder\\PMP BRGS\\0845102'},
 {'id': 20397,
  'name': 'PMP BRGS',
  'active': True,
  'parent': 1,
  'description': '',
  'path': 'Root Folder\\PMP BRGS'},
 {'id': 1,
  'name': 'Root Folder',
  'active': True,
  'parent': 0,
  'description': '',
  'path': 'Root Folder'}]
```
 

## Trend

```python
result = client.get_trend_measurements(nodeID) # to collect trend data
pd.DataFrame(result).to_csv('meas.csv')
```

# Pipelines and Database Synch
The get_sync_measurements() function is a specialized utility for efficiently retrieving data from the Observer application. It uses a synchronization marker to ensure data is retrieved chronologically, without relying on timestamps. This method prevents the omission of records that might arrive out of order, which is a common problem with timestamp-based data collection.

## Functionality
This function operates in a cyclical, stateful manner:

1- API Call: It internally makes a call to the Observer API to fetch new data.

2- Data Retrieval: It collects all new records of the specified data_type that have been added to the database since the last API call.

3- Synchronization: The function automatically updates an internal synchronization marker, noting the last record's unique ID. This marker is then used as the starting point for the next call.


### Key Features
1- Auto Token Renewal: The client function is already equipped with an automatic token renewal mechanism. This feature ensures uninterrupted data flow by automatically refreshing the API authentication token before it expires, eliminating the need for manual token management within your application code.

2- Synchronization Marker: Instead of relying on timestamps, the function uses a synchronization marker. This marker is a unique ID of the last record received, ensuring that the next API call starts precisely where the last one left off. This guarantees that no records are missed, even if they arrive out of sequence.

3- Scalability: The function is designed for large-scale data retrieval. It can handle continuous data streams and is optimized to pull large initial batches of data to catch up quickly, then transition to smaller, more frequent pulls to stay current.

## Usage
The get_sync_measurements() function is ideal for building data pipelines that require a continuous, real-time feed from a database. 
```python
data = client.get_sync_measurements('trend')
```

The provided example demonstrates a simple loop that repeatedly calls the function to stay synchronized with the Observer database.


```python
print("start:", client.syncMarker_trend)
while 1:
    startingSynchMarker = client.syncMarker_trend
    data = client.get_sync_measurements('trend')  # actual action here
    EndingDate = data[-1]["ReadingTimeUTC"]
    print("New data size: ", len(data), ", synch From:", startingSynchMarker, ", synch to:", client.syncMarker_trend, ", data to date: ", EndingDate)
    time.sleep(10)
```
Output and Interpretation
The sample output below illustrates the function's behavior:

- Initial Calls: The first several calls retrieve a large number of records (e.g., 10000). This indicates the function is catching up on historical data from its starting point (synch From: 0). The EndingDate shows a significant jump forward in time with each large batch.

- Final Calls: As the loop progresses, the number of new records decreases (1708, then 54, then 27). This signifies that the pipeline is now in sync with the database. It is only retrieving new data as it is being added, effectively providing a real-time stream.

![alt text](synchMarkerOutputSample.png)


## Pipelines Full Example
Data Synchronization Pipeline
This document describes a Python script designed to create an efficient and robust data synchronization pipeline for retrieving data from the SKF Observer application. The pipeline utilizes a multithreaded approach to handle multiple data streams concurrently, ensuring that both "Trend" and "Dynamic" data are kept up-to-date with the database.

### Key Features
- Multithreaded Execution: The script uses Python's threading module to run two independent loops in parallel, one for trend data and one for dynamic data. This concurrency prevents one data stream from blocking the other, maximizing data retrieval efficiency.

- Synchronization Markers: Instead of relying on timestamps, the get_sync_measurements() function uses synchronization markers to ensure no records are missed. Each thread maintains its own marker (client.syncMarker_trend and client.syncMarker_dynamic), which is automatically updated after each successful API call.

- Non-overlapping API Calls: A randomized delay is added to the time.sleep() function (10 + random.uniform(0, 5) and 15 + random.uniform(0, 5)). This helps prevent a flood of simultaneous API requests, reducing the load on the database and preventing potential timeouts or throttling.

- Automatic Token Renewal: The underlying skfobserver.APIClient is equipped with an automatic token renewal mechanism. This means the authentication token is automatically refreshed before it expires, ensuring the pipeline can run continuously without manual intervention.

### Code Structure
The script is composed of two main functions, each running in a separate thread:

- getTrend(): A continuous loop that retrieves trend data. It prints the number of new records, the synchronization marker used for the call, the new synchronization marker, and the timestamp of the latest record.

- getDynamic(): A continuous loop that retrieves dynamic (waveform) data. Similar to the getTrend() function, it provides detailed output for monitoring.

The if __name__ == "__main__": block serves as the main entry point, where the two threads are created and started. This ensures the code only runs when the script is executed directly.


```python
import skfobserver
import threading # import multi-threading
import time 
import random # add rand time to not overalaping the api calls


client = skfobserver.APIClient(profile_name="myConnection")
 
def getTrend(): 
    while True:
        startingSynchMarker = client.syncMarker_trend
        data = client.get_sync_measurements('trend') # get trend data
        if(len(data) != 0):
            print("TREND: New data size: ", len(data), ", synch From:", startingSynchMarker, ", synch to:", client.syncMarker_trend, ", data to date: ", data[-1]["ReadingTimeUTC"])
        else:
            print("TREND: No new data found")        
        time.sleep(10 + random.uniform(0, 5))  
 
def getDynamic():
    while True: 
        if(len(data) != 0):
            startingSynchMarker = client.syncMarker_dynamic
            data = client.get_sync_measurements('dynamic')  # get waveform data (Dynamic)
            print("Dynamic: New data size: ", len(data), ", synch From:", startingSynchMarker, ", synch to:", client.syncMarker_trend, ", data to date: ", data[-1]["ReadingTimeUTC"])
            time.sleep(15 + random.uniform(0, 5)) 
        else:
            print("Dynamic: No new data found")
            


if __name__ == "__main__": 
    thread1 = threading.Thread(target=getTrend)
    thread2 = threading.Thread(target=getDynamic) 

    thread1.start()
    thread2.start() 

```



### Sample Output
The output below demonstrates the parallel execution of the two threads. You can see how each data stream (TREND and Dynamic) is processed independently, with its own synchronization marker being updated. Initially, the script pulls a large number of records to get up to date, then settles into pulling smaller, more frequent batches as it becomes in sync with the live data feed.

![alt text](pipelineExample.png)