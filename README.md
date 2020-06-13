## Recommovie

![homepage](/img/homepage2.png)


## Installation and Usage
For all of options, clone the repository,

```bash
$ git clone https://github.com/egemenzeytinci/recommovie.git
```

### Option 1: Use existing db
1.  Build and run the docker:

    ```bash
    $ docker-compose build && docker-compose up -d
    ```

2.  And check containers with this command:

    ```bash
    $ docker container ls
    ```

    You will see 2 containers named **app** and **elastic**.

3.  Lastly, check **localhost:5002**

### Option 2: Crawl another movies
1. Download IMDB datasets:
 
    ```bash
    $  wget https://datasets.imdbws.com/title.basics.tsv.gz -P imdb/data/
    $  wget https://datasets.imdbws.com/title.ratings.tsv.gz -P imdb/data/
    $  wget https://datasets.imdbws.com/title.episode.tsv.gz -P imdb/data/
    ```
    
2.  Run the code for creating db only once:

    ```bash
    $  python3 db/models.py
    ```
    
3.  Run the code for crawler:

    ```bash
    $  python3 crawl.py
    ```

4. Then, apply steps in option 1.

**PS:** Do not use the full data. Because, that's take a long time.

### Option 3: Manuel usage
1. Download and install elasticsearch:
 
    ```bash
    $  wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-6.6.1.tar.gz
    $  tar -xf elasticsearch-6.6.1.tar.gz
    $  cd elasticsearch-6.6.1
    $  ./bin/elastichsearch
    ```
    
2.  Run the code for app:

    ```bash
    $  python3 app.py config.ini
    ```

**PS:** Change the host of elasticsearch, from *elastic* to *localhost*





