## Recommovie
###### Recommovie &bull; Egemen Zeytinci &bull; 09/2018
---

![homepage](/img/homepage.png)


## Installation
---
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