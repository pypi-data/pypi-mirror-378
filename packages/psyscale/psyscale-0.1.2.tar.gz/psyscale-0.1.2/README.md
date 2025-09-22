Psyscale
========

PsyscaleDB is a Python library designed for efficient storage, querying, and management of financial timeseries data using a TimescaleDB-accelerated PostgreSQL backend. Built on top of psycopg and tightly integrated with pandas, it offers a simplified interface for working with financial timeseries datasets in the form of DataFrames. 

### Features :
- Full Asyncio Support.
- Search Symbols / Tickers by relevance.
- Store and Retrieve Timeseries data by Trading Session. 
    - Utilizes pandas_market_calendars for Trade Session Identification.
- 100% Configurable to store and/or aggregate data at any timeframe, including Tick Level Data
- Supports timeframe aggregation upon request to allow for custom Storage/Real-time Computation Trade-offs.
- CLI Script Functions to aid Database Configuration & Refreshing Aggregates.
- Composition Approach to class structure to allow for custom database expansion by extending the PsyscaleDB Class.

> Note: At the moment the library has only been tested and used in a windows environment. Mac/Unix environment functionality is not guaranteed.

## Installation
```
pip install psyscale
```

# Getting Started

Getting Started should be very easy if a postgres database already exists for you to connect and inject data into. If so, skip forward to "Step #2: Connecting".

Throughout database manipulation it is helpful to confirm the changes made in the database through a GUI. For this, TablePlus can be used to see and manually query
the database. Currently all data can be found under the following four schemas: 'security', 'tick_data', 'minute_data', and 'aggregate_data'.

## Step #1: Creating a PostgreSQL Client
Psyscale requires connecting to a PostgreSQL Client. The easiest method for initializing one is through Docker.
Only a Single Container is required, and it can be generated from the standard TimescaleDB Image.


### Manual Host Initilization
----
You can manually pull and launch a local docker container using the following commands.
If this is done, the docker container must be manually run prior to using Psyscale if it ever shuts down.
Mounting the volume to a location on your local machine will allow the data to persist between restarts.

```
docker pull timescale/timescaledb-ha:pg17
```

```
docker run 
    -d --name timescaledb 
    -p 5432:5432 
    -e POSTGRES_PASSWORD=password
    -v [*desired storage location*]:/home/postgres/pgdata/data
    timescale/timescaledb-ha:pg17 
```
To connect to this database you can use the parameters individually or the following connection URL:

```
"postgresql://postgres:password@localhost:5432/timescaledb"
```

### Automatic Local Host initilization w/ Docker Compose.
----
This library contains a docker compose .yml file the sets up the minimum required docker container. 
This is the preferred method, as it allows the Pyscale client to execute 'docker up' to ensure the required local host
is running in the event it shuts down or the local machine has been restarted.

For this to work, the desired connection parameters *must* be loaded as individual environment variables. Both the Docker Compose .yml and Psyscale Client
can use these environment variables to start and connect to a localhost.

```
## .env file
PSYSCALE_PORT = "5432"
PSYSCALE_HOST = "localhost"
PSYSCALE_USER = "postgres"
PSYSCALE_PASSWORD = "password"
PSYSCALE_DB_NAME = "mydb"
PSYSCALE_VOLUME_PATH = 'E:/TimescaleDB'
```

When the above is supplied and loaded, the Psyscale Client will attempt to connect. When/if it fails, but has the above environment variables, it will
make the given volume mount directory (when needed) and then use subprocess to call:
```
docker pull timescale/timescaledb-ha:pg17                 # Only called when image is needed
docker-compose -f [file_path_to_psyscale_install_location]./timescale.yml up -d 
```

Python Code for docker-compose localhost initilization:
```python
import dotenv  # Included when installing psyscale
from psyscale import PsycaleDB

dotenv.load_dotenv(dotenv.find_dotenv())
db = PsyscaleDB()
```

If desired, a custom Docker-Compose file can be used by providing an absolute file path to the psyscale client at initilization.
```python
...
db = PsyscaleDB(
    docker_compose_fpath = "[absolute file path to a custom .yml file]"
)
```

## Step #2: Connecting to a Database
### Method #1 : Connection Parameters
```python
from psyscale import PsyscaleDB, PsyscaleConnectParams

params = PsyscaleConnectParams(
    host = 'localhost',
    port = 5432,
    user = 'postgres',
    password= 'password',
    database= 'mydb',
)
db = PsyscaleDB(params)
```

### Method #2 : Connection URL
```python
from psyscale import PsyscaleDB

# Postgres URL Format : "postgresql://{username}:{password}@{host}:{port}/{database}"
db = PsyscaleDB(
    "postgresql://username:password@localhost:5432/mydb"
)
```


### Method #3 : Environment Variables

#### Environment Variables File (.env)
```.env
PSYSCALE_URL = "postgresql://{username}:{password}@{host}:{port}/{database}" (Not Compatible w/ Docker-Compose)
# -- OR -- 
PSYSCALE_PORT = "5432"
PSYSCALE_HOST = "localhost"
PSYSCALE_USER = "postgres"
PSYSCALE_PASSWORD = "password"
PSYSCALE_DB_NAME = "mydb"

PSYSCALE_VOLUME_PATH = 'E:/TimescaleDB' (Only needed when Psyscale is set to use Docker Compose)
```
#### Python file
```python
import dotenv # Included when installing psyscale
from psyscale import PsyscaleDB

dotenv.load_dotenv(dotenv.find_dotenv())
db = PsyscaleDB()
```


## Step #3: Database Configuration
There exists three different schemas in the database for storing data: TICK_DATA, MINUTE_DATA, AGGREGATE_DATA

They are all functionally equivelant and can each be configured in anyway or not at all. Their intent is to delineate between
the types of data that can be retrieved from a data broker.

For an Executable Script see ./examples/configure_db.py in the github repository.


- TICK_DATA
    - Stores Data at the Tick level, all aggregates are computed, cumulatively, from this source of data.
    - Data only goes as far back as the first piece of Tick Data.
    - Can compute Aggregates of 1 second and higher. 
- MINUTE_DATA
    - Stores Data at the 1 Minute Timeframe, All aggregates are computed, cumulatively, from this source of Data.
    - Data only goes as far back as the first piece of Minute Data.
    - Can Compute Aggregates of 1 minute or higher to a resolution of 1 minute.
    - Applies to Data Brokers such as Alpaca & Polygon.io
- AGGREGATE_DATA
    - Stores data at all desired Timeframes. Aggregates are not computed unless desired at runtime.
    - Data goes further back in time at higher timeframes than at lower timeframes. 
    - *All* Data tables need to be retrieved and stored when refreshing database.
    - Can compute Aggregates at runtime to a resolution of the minimum store timeframe.
    - Applies to Data Brokers such as YFinance where Higher timeframe (HTF) data has more history than Lower Timeframe Data (LTF)


## TimeseriesConfig
Configurations are managed through the TimeseriesConfig Object. See the Class Docstring for a full argument description.
```python
CONFIG = TimeseriesConfig(
    asset_types : List[str] # e.g. Crypto, Forex, us_stock ...
    rth_origins: Dict[asset_type: pandas Timestamp] # RTH origin Timestamp per asset type
    eth_origins: Dict[asset_type: pandas Timestamp] # ETH Origin Timestamp per asset type
    prioritize_rth: Dict[asset_type: bool | None] # What to store when RTH/ETH aggregates conflict
    # Each Timeseries Table Stores multipel symbols, 
    # Data Tables are grouped by asset_type & Timeframe, i.e. all Crypto @ 5 Min intervals
    calculated_periods : Dict[asset_type: List[Pandas Timedeltas]] # Continuous Aggregates to Calculate, per asset type
    stored_periods : Dict[asset_type: List[Pandas Timedeltas]] # Data to Insert per asset type
)
```
#### Example Configurations
Tick Data: 
- Stored Periods only include Timedelta(0)
- Calculated Periods can be as small as '1s' & have '1s' resolution
```python
from pandas import Timestamp, Timedelta
from psyscale import TimeseriesConfig

STD_TICK_CONFIG = TimeseriesConfig(
    ['us_stock', 'us_fund', 'crypto', 'forex'],
    rth_origins={
        "us_stock": Timestamp("2000/01/03 08:30", tz="America/New_York"),
        "us_fund": Timestamp("2000/01/03 08:30", tz="America/New_York"),
        # "default": Timestamp("2000/01/03 00:00", tz="UTC") :: Implicit, but overridable 
    },
    eth_origins={
        "us_stock": Timestamp("2000/01/03 04:00", tz="America/New_York"),
        "us_fund": Timestamp("2000/01/03 04:00", tz="America/New_York"),
        # "default": Timestamp("2000/01/03 00:00", tz="UTC") :: Implicit, but overridable 
    },
    prioritize_rth={"us_stock": True, "us_fund": None},
    calculated_periods={
        "default": [
            Timedelta('1s'), # Can store down to '1 second' timeframes
            Timedelta('30s'),
            Timedelta('1min'), 
            ...
            ],
        },
    stored_periods={"default": [Timedelta(0)]},
)
```

Minute Data: 
- Stored periods only includes Timedelta('1min')
- Calculated Periods are only greater than '1min'
```python
from pandas import Timestamp, Timedelta
from psyscale import TimeseriesConfig

STD_MINUTE_CONFIG = TimeseriesConfig(
    [...], # Same as Above
    rth_origins = { ... }, # Same as Above
    eth_origins = { ... }, # Same as Above
    prioritize_rth= { ... } # Same as Above
    calculated_periods={
        "default": [
            Timedelta('5min'), # Can store anything above '1 minute'
            Timedelta('15min'), # at increments of '1 minute'
            Timedelta('30min'), 
            ...
            ],
        "crypto": [ # Optionally Specifiy different times per asset type
            Timedelta('30min'),
            Timedelta('1h'),
            Timedelta('4h'), 
            ...
            ],
        },
    stored_periods={"default": [Timedelta('1min')]},
)
```


Aggregate Data: 
- While not explicity required, there are no Calculated Periods.
    - Querying and storing the timeframes allows for more data to be stored at higher timeframes so is more ideal.
- All desired timeframes are under Stored Periods.

```python
from pandas import Timestamp, Timedelta
from psyscale import TimeseriesConfig

STD_AGGREGATE_CONFIG = TimeseriesConfig(
    [...], # Same as Above
    rth_origins={ ... }, # Same as Above
    eth_origins={ ... }, # Same as Above
    prioritize_rth= { ... } # Same as Above
    calculated_periods={[]},
    stored_periods={"default": [
            Timedelta('1min'),
            Timedelta('30min'),
            Timedelta('4h'),
            Timedelta('1D'),
            ...
        ],
    },
)
```

### Applying Configurations:
The above configurations can be applied to the database using the 'configure_timeseries_schema' method.
This is a CLI Interface method that will Add, Update, & Delete the relevant timeseries tables. 

A working version of this script can be found in the github repository under ./examples/configure_db.py
```python
from psyscale import PsyscaleDB
db = PsyscaleDB()

# CLI Method to manage setting and changing Data Configurations
# Only needs to be run once, or when changes are desired.
db.configure_timeseries_schema(
    tick_tables=TICK_CONFIG, # or None
    minute_tables=MINUTE_CONFIG, # or None
    aggregate_tables=AGGREGATE_CONFIG, # or None
)

```

## Step #4: Symbol Data Insertions & Maintenance
At this point the database is fully configured and just awaiting symbol & timeseries data.

Alpaca's API & the alpaca-py python library can be used to test data insertions for free.

A working example of Symbol data insertions can be found in the github repository under ./examples/import_symbols.py.
The process, generically, is as follows:

```python
from pandas import Dataframe
from psyscale import PsyscaleDB
from alpaca.trading.client import TradingClient


alpaca = TradingClient(
    api_key = os.getenv("ALPACA_API_KEY"),
    secret_key =os.getenv("ALPACA_API_SECRET_KEY"),
    raw_data = True, paper=True
)

json_assets = alpaca.get_all_assets() 
df_assets = Dataframe(assets_json).set_index("id")

'''
df_assets contains columns: ['cusip', 'class', 'exchange', 'symbol', 'name', 'status', 'tradable', ...etc]
Filter this down to only columns: ['asset_type', 'symbol', 'exchange', 'name', ...etc]
Those 4 columns are required, and 'asset_type' must match the asset_types passed in 'configure_timeseries_schema'
Excess Column will be packaged into an 'attrs' column in the database. 
These additional attributes can be searched later on
'''

db = PsyscaleDB()
inserted, updated = db.upsert_securities(
    symbols = df_assets_filtered, 
    source = "Alpaca", # Since all these symbols were pulled from alpaca
)
print(inserted) # Series of unique symbols inserted.
print(updated) # Series of entries updated based on 'source', 'symbol' & 'exchange' uniqueness collisions.

```

```python
# search symbols to return information from the database. See method Docstring for more info.
db.search_symbols()
```


## Step #5: Timeseries Data Insertions & Maintenance
Data insertions are associated with a symbol's primary key, which is generated when a symbol is inserted into the database as done above.

Symbol pkeys are given based on a unique Symbol, Exchange, & Source combination.

To store timeseries information for a symbol, it must first be set to be stored. There are 3 boolean columns in the symbols table
that define which schema the primary key is stored in: store_tick, store_minute, store_aggregate. 
Each Pkey can only be stored in one of the three data schemas: tick, minute, aggregate.


To set this store state you can use the following:
```python
db = PsyscaleDB()
db.update_symbol(
    symbols: = 'SPY' # Case insenstive, can be a symbol, pkey, or list of symbols / pkeys
    args = {'store_minute': True} # The argument to update
)
```

The database is designed to be periodically updated by a scheduleable python script. If live data is needed it is intended for that data to be
 joined with the historical data stored in the database.

A working example of Symbol data insertions can be found in the github repository under ./examples/import_symbols.py. The process, generically, is as follows:

```python
db = PsyscaleDB()
alpaca_api = AlpacaAPI()

# Search all symbols for those that are set to store TimeseriesData
# Do this grouped by data-brokers so data only needs to be fetched from one data source at a time
symbols = db.search_symbols(
    {
        "source":"Alpaca",
        "store": True,
    },
    limit = None
)

# Loop through though symbols to fetch all the data that is needed.
for symbol in symbols:
    # Metadata is a Dataclass that has the stored date range for a symbol, per timeseries table.
    symbol_metadata_list = db.stored_metadata(
        pkey = symbol["pkey"], # Symbol Primary Key
        filter = {'is_raw_data':True}, # Filter for only tables that are raw inserted data
        _all = True, # Flag to return metadata for tables that should have data for this symbol, but don't yet.
    )

    # Loop through each MetadataInfo Obj to update each table that needs it's stored data updated.
    for metadata in symbol_metadata_list:

        # Fetch the desired data:
        data_df = alpaca_api.get_hist(
            symbol["symbol"],
            metadata.timeframe, # Time period the fetch 
            start=metadata.end_date, # Only fetch data newer than what is stored.
        )

        '''
        Aggregate Data 
        Requires: Timestamp & Close columns
        Accepts: Open, High, Low, Volume, Ticks, & VWAP columns

        Ticks Data
        Requires: Timestamp & Price Columns
        Accepts: Volume Column
        '''

        # Insert it into the database.
        db.upsert_series(
            symbol["pkey"],
            metadata, # Used to determine what Table and Schema the data should be inserted into
            data_df, # The dataframe will be formatted as needed. For the most part it will detect what data has been given.
            symbol['exchange'], # Used with pandas_market_calendars to determine RTH/ETH Trading Sessions.
        )

'''
Repeat the above process for any other data-brokers that have timeseries data stored in the database.
'''

# Automatically refreshes all Continuous Aggregates and the Metadata Table
# based on how what timeseries data was stored.
db.refresh_aggregate_metadata()

# If this was not called before the PsyscaleDB client was deleted, 
# The following CLI Interface method can be called to selectively, or
# bulk, update the continuous aggregates & Metadata Table.
db.manually_refresh_aggregate_metadata()

```