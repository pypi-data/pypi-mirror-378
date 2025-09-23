
# Table of Contents

1.  [SQLite Database](#org7c02cbe)
    1.  [Datasets currently included:](#orge88c16b)
2.  [Key Features](#orgda9a069)
3.  [Installation](#org0ae2129)
4.  [How to use with examples](#org94cd2fd)
    1.  [Browsing Metadata](#org89a166a)
    2.  [Visualization](#orgf9cf6be)
    3.  [Generate Data](#org6e8f9a4)
5.  [Advanced: Managing the database](#org213a1d3)
    1.  [Reindexing](#orge03e052)
    2.  [(Re)compile the database](#org841514e)
6.  [Support and contact](#org87c7675)
7.  [Contribution](#org2896907)
8.  [Acknowledgments](#org7ea1cbb)

This Python module provides an efficient SQLite database for browsing, visualizing and processing Internal Reflecting Horizons (isochrones) across Antarctica, curated by the AntArchitecture action group. It is specifically designed for ice dynamic modelers who need a fast, memory-efficient data structure to constrain their models.


<a id="org7c02cbe"></a>

# SQLite Database

The database uses SQLite for efficient indexing. Data is sourced from the associated DOIs and stored as binary DataFrame files for each layer (IRH) and trace ID. This structure enables:

-   Browsing by author (region), layer age, or trace ID.
-   Memory efficiency: Only relevant data is read when needed.
-   Fast read performance: Lightweight and optimized for speed.


<a id="orge88c16b"></a>

## Datasets currently included:

-   Winter et al. 2018, (<https://doi.org/10.1594/PANGAEA.895528>)
-   Cavitte et al. 2020, (<https://doi.org/10.15784/601411>)
-   Beem et al. 2021, (<https://doi.org/10.15784/601437>)
-   Wang et al. 2023, (<https://doi.org/10.1594/PANGAEA.958462>)
-   Sanderson et al. 2024, (<https://doi.org/10.5285/cfafb639-991a-422f-9caa-7793c195d316>)
-   Franke et al. 2025, (<https://doi.org/10.1594/PANGAEA.973266>)


<a id="orgda9a069"></a>

# Key Features

-   Efficient SQLite indexing
-   Quick visualization on Antarctica map
-   Generate lazy data for later use


<a id="org0ae2129"></a>

# Installation

1- Clone this repository:

    git clone git@github:antoinehermant/anta_database.git
    cd anta_database

2- Create a specific python environment (optional but recommended):

    '''Using conda'''
    conda create -n anta_database
    conda activate anta_database
    conda install pip
    
    '''Using venv'''
    python -m venv /path/to/environment/anta_database # Replace the path with your desired environment path
    source /path/to/environment/anta_database

3- Install the Python module:

    pip install .

Note: The database is not included in this repository. Contact me for access.


<a id="org94cd2fd"></a>

# How to use with examples

Also see the Jupyter Notebook &rsquo;example.ipynb&rsquo; for a more integrated tutorial.


<a id="org89a166a"></a>

## Browsing Metadata

-   First, initialize the Database class:

    from anta_database import Database
    database = Database('/path/to/AntADatabase/') # insert the path of the downloaded database, absolute path is recommanded

Then use the query() function to browse the database. query() without argument will return all metadata from the database:

    database.query()

By default, a dictionary with all available trace IDs is included in the query results. This can seem a lot, but it is actually useful for grepping traces with descriptive names such as &rsquo;DC<sub>LDC</sub><sub>DIVIDE</sub>&rsquo;.

-   Refine your search either by author, age, or trace<sub>id</sub>, or by combining arguments. Lists are also allowed:

    database.query(author='Cavitte_2020') # all data from Cavitte et al. 2020
    database.query(age='38100') # all datasets with the 38.1ka isochrone
    database.query(var='IceThk') # all datasets with IceThk variable
    database.query(trace_id='DC_LDC_DIVIDE') # all layers with the trace ID DC_LDC_DIVIDE
    database.query(author=['Franke_2025', 'Winter_2018'], age='38100') # example of multiple criteria

Note: &rsquo;IceThk&rsquo;, &rsquo;SurfElev&rsquo; and &rsquo;BedElev&rsquo; are possible extra variables included in the database when the datasets contain the relevant data.


<a id="orgf9cf6be"></a>

## Visualization

Use the results of the query in the plotting functions:

    results = database.query(age='38100')
    database.plotXY(results,
                    downscale_factor=1000, # downscale the datasets n times, which makes no visual difference but it is much lighter
                    title='AntArchitecture 38.1ka layer',
                    xlim=(-500, 2400), ylim=(-2200, 2200), # set the plot extent in km
                    scale_factor=0.5, # adjust the size of the plot
                    latex=True, # use latex compilers for plotting if you have them installed on your system
                    # save='AntA_38ka.pdf', # Uncomment to save the figure, otherwise it we visualize with pyplot
                    )

![img](./anta_database/figures/AntA_38ka.png "Example figure")


<a id="org6e8f9a4"></a>

## Generate Data

Note: This part could be developed further in the future if there is the need. But for now, I am designing a separate Python module for constraining my ice sheet model of use, which is tailored to this database and other parallel processing libraries.

The data<sub>generator</sub>() function reads the query and &rsquo;yield&rsquo; the dataframes for later use.
Here is a quick example of how this can be used for computing the mean layer depth:

    results = database.query(age='38100')
    lazy_dfs = database.data_generator(results)
    
    mean_depth_trs = []
    for df, md in lazy_dfs:
        mean_depth_trs.append(np.mean(df['38100']))
    
    mean_depth = np.mean(mean_depth_trs)
    print('The mean depth of the 38ka isochrone across East Antarctica is', mean_depth, 'm')

The downscale<sub>factor</sub> argument in the data<sub>generator</sub> reduces the size of the generated data by n times. This is useful when dealing with large data where the downscaling has a neglectable influence on the results:

    lazy_dfs = database.data_generator(results, downscale_factor=10)

Note: In the database, the file paths are relative to the database path. When initiating the database, you provide the absolute path to the database. So the data<sub>generator</sub> function uses the relative path given in the results from the query and the absolute path to the database to read the files. The second argument returned by data<sub>generator</sub> (&rsquo;md&rsquo; in the example above) is the unique metadata for the current df.


<a id="org213a1d3"></a>

# Advanced: Managing the database


<a id="orge03e052"></a>

## Reindexing

You may want for example to update the age of the layers in a particular dataset.
For this, you just need to modify the ages in the file called &rsquo;IRH<sub>ages.tab</sub>&rsquo; located under a dataset directory. Then, reindex with the IndexDatabase class:

    from anta_database import IndexDatabase
    
    db_path = '/path/to/root/of/the/database/' # path to 'AntADatabase/'
    indexing = IndexDatabase(db_path)
    indexing.index_database()


<a id="org841514e"></a>

## (Re)compile the database

You can (re)compile the database, if for example you modify some data in the raw directories or if you add a dataset.
For this, make sure to follow the structure:

    AntADatabase/
    ├── AntADatabase.db
    ├── database_index.csv #List of directories to index: Author_YYYY,Author et al. YYYY,doi
    ├── Author_YYYY
        ├── IRH_ages.tab #IRH file names without .ext followed by there respective age in years
        ├── original_new_column_names.csv #first row: names of columns to keep from raw files, second row: how the columns should be renamed
        ├── raw/
        └── pkl/

Then use the CompileDatabase class to compile the database.

    from anta_database import CompileDatabase
    
    dir_path_list = [ # list of the dataset subdirectories to compile
        './Winter_2018',
        './Sanderson_2024',
        './Franke_2025',
        './Cavitte_2020',
        './Beem_2021',
    ]
    
    compiler = CompileDatabase(dir_path_list)
    compiler.compile()

Then reindex (see above).
By default, it assumes that the files in raw/ are sorted by IRH (one file = one layer and multiple traces). If the files are sorted the other way around (one file = one trace and multiple layers), you can set file<sub>type</sub>=&rsquo;trace&rsquo; in CompileDatabase(). Furthermore, if the depth is not given in meters but TWT, you should set the wave<sub>speed</sub> (units should match values in the file) for conversion and firn<sub>correction</sub> (meters):

    dir_path = './Wang_2023'
    compiler = CompileDatabase(dir_path, file_type='trace', wave_speed=0.1685, firn_correction=15.5)
    compiler.compile()


<a id="org87c7675"></a>

# Support and contact

You can email me for downloading the database: antoine.hermant@unibe.ch

Feel free to raise an issue on the GitHub if you find any bug or if you would like a feature added.


<a id="org2896907"></a>

# Contribution

If you like this database and wish to help me develop this module, do not hesitate to contact me. You should then fork the repo, build feature branches and pull request. That would be much appreciated!


<a id="org7ea1cbb"></a>

# Acknowledgments

I am developing this tool as part of my PhD project, which is funded by the Swiss National Science Foundation (grant no. 211542, Project CHARIBDIS)
Any data used through this database should be cited at source. For this, use the DOI provided in the metadata.
If you used this tool for your work and this was useful, please cite this repo, so other people get to know that it exists.

