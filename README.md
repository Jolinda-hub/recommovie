

# recommovie  
  
Firstly, if not installed;  
```  
pip install virtualenv  
virtualenv /path/to/virtualenv  
source /path/to/virtualenv/source/bin/activate  
pip install -r /path/to/recommendation/requirements.txt  
```  
  
This project aims,  
  
1. **IMDB Crawler:** You can run the command ````python imdb/main.py````  for crawler. 
The start year was selected as 1900 in **append** method  in **crawler.py** You can change this year.  

	Sample url for request:   
<i>https://www.imdb.com/search/title?user_rating=1.6,2.0&year=2010&start=1</i>  

	User rating between lower bound and upper bound (1.6-2.0, 2.1-2.5 etc.), because **404 page not found** 
error returns after 10.000 movies. The processing time depends on the year you specify. It is foreseen to last long.

	**NOTE:** Run the models.py file only once, and above all, run it.

2. **Recommendation:** You can run the command ````python recommendation/main.py````  for recommendation system. 
You will see the following code in **main.py**:

	```movie_df = movie_df[movie_df.kind == 1]```

	kind = 1 movies, kind = 0 represents the series. If you want to receive both, your memory of device 
may not be enough. You can try to use the limit.

Finally, check the two tables under the recommendation db after run the ````python imdb/main.py```` 
and ````python recommendation/main.py````



