
# A.I. Legal Research Assistant

[__Fall 2017 Galvanize Data Science Immersive__](https://www.galvanize.com/austin)

An Investigation of legal research using the court cases scraped with Python's Beautiful Soup from FindLaw.com.

__Abstract:__ This project uses over 6,000 U.S. Supreme Court and U.S. Circuit Courts of Appeals' immigration cases. These were scraped using Python's Beautiful Soup from FindLaw.com on Amazon AMIs and S3. 

__Results:__ Built a fully functioning legal search engine able to take in free text queries and return relevant results based on cosine similarity built on Tf-IDF weights. Additionally, each result has 3 related court cases based on Networkx graph recommendations. 

See this work as a presentation in [Google Slides](https://docs.google.com/presentation/d/18PTXyDBYRlwHm7m53Z7BVN3Ix4OfCYLWLPpcTeVV6Is/edit?usp=sharing).

[See the video](https://www.youtube.com/watch?v=o5R0kOjtzwA&index=5&list=PLxtztEze-DRfCd2LY4IRytALcjpJQp0WC) of this talk.


## Motivation: 

Any U.S. citizen is entitled to legal representation under the law. The same is not true for non-citizens. In immigration court, over 80% of all defendants go unrepresented simply because they cannot afford a lawyer. Legal research stands among the highest costs for defendants. To illustrate, below are the national average of hourly rates for divorce attorneys: 

<p align="center"> 
<img src="https://github.com/305kev/Capstone_Proposal/blob/master/images/histogram_0.png" width=75% height=75% />

<br> Figure 1. Distribution of hourly rates for divorce attorneys, https://www.nolo.com/legal-encyclopedia/ctp/cost-of-divorce.html


## The Problem:
One of the big problems in the legal industry is the amount of time lawyers spend on legal research. It is not uncommon for lawyers to spend up to 25% or even 50% of their time engaged in this activity, as shown by the pie chart on the left. [fig 2]. Another issue highlighted by the chart on the right is the complexity of the query search terms necessary to achieve relevant results.[fig 3] The question is, can a system be built to achieve high precision (the portion of truly relevant results that are shown) and high recall (the portion of all truly relevant) results? 

<br>

<img src="https://github.com/305kev/Capstone_Proposal/blob/master/images/pie.png" width="425"/><img src="https://github.com/305kev/Capstone_Proposal/blob/master/images/current_searches.png" width="425"/>

<br> Figure 2. Average time spent on legal research, http://bit.ly/1vfqzm3
<br> Figure 3. Current legal search queries, https://lscontent.westlaw.com/images/content/WLNT&CSearching.pdf 

<br>


## Potential Solution (Demo): 
This is where A.I. steps in. Although recent advances in machine learning have affected most major industries, the legal market is notably absent, with a few exceptions. ROSS A.I. is a startup company that has built a search engine built to optimize legal research; however they are solely focused on bankruptcy law. With this project, I intend to build upon their work and expand this ML powered search engine to new areas like immigration law. Below is an example of how it works: 
<br> 
<p align="center"> 
<img src="https://github.com/305kev/Capstone_Proposal/blob/master/images/demo.gif" width=75% height=75% />
<br> Figure 4. Legal A.I. search engine by Kevin G. Magana, a demonstation of the product
</p>


## The Process: 

<p align="center"> 
<img src="https://github.com/305kev/Capstone_Proposal/blob/master/images/pipeline.png" width=75% height=75% />
 <br> Figure 5. Legal A.I. search query pipeline
</p>


One of the biggest hurdles to overcome is how to access all the relevant data. Using $15 per search engines like Westlaw and LexisNexis are not feasible, however convenient their aggregation of all relevant law types may be. Alternatively, it is possible to set up web-scrapers to access and store the data held piecemeal on many government websites and free legal resource sites like FindLaw. That is how I begin my data collection. Using Python's Beautiful Soup module, I scraped over 6,000 cases using a cadre of AWS EC2s, and saved the results as csv files in Amazon's S3 bucket service. Below is an example of how I stored the scraped court case data: 


<p align="center"> 
<img src="https://github.com/305kev/Capstone_Proposal/blob/master/images/df.png" width=75% height=75% />
 <br> Figure 6. Legal A.I. example of how cases are stored in pandas dataframes
</p>


Next, I indexed the cases in such a way as to make it easy to locate all the court documents where each term in the query appears. In addition, I added the position/ index where each term appears in the court document, to enable phrase searching (ex: "United States of America" or "New York Yankees"). Below is an example: 

<p align="center"> 
<img src="https://github.com/305kev/Capstone_Proposal/blob/master/images/index.png" width=75% height=75% />
 <br> Figure 7. Legal A.I. court case search index
</p>

In order to get the entire set of unique terms in the corpus of court cases, I passed in each case through a standard Natural Language Processing "cleaning" process that involves removing punctuation, common "stop words" that do not help in differentiating between court cases, and also stemming (getting the root word for each term; ex: run, instead of running). 
To enable an "apples to apples" comparison, I ran the same process through the search query. 

After the data had been fulled indexed, (1) I was able to get the user query and run it through a spell correction and free text query parser, which was exactly the same process I ran on the court cases. (2) This enabled me to implement the searching and matching of cases with respect to the query terms. As an initial model, (3) I used the intersection of the sets of matching court cases per query term -- so no case will show up unless all the relevant, cleaned query terms appeared in the text. Having created a Tf-IDF matrix as part of the data processing pipeline in figure 5, (4) I grabbed the matched cases from the index and created a created a subset Tf-IDF matrix of only the matched cases. (5) This then made it possible to run a Cosine Similarity function of these cases against the query itself to return a list of cases in descending order of similarity, which, in a simple, initial model, gave me the results page necessary for Legal A.I. 1.0. 

## The Challenge: 

The types of law pose a domain-knowledge challenge as well as a programmatic one. For the domain-based knowledge, I am working with several law students as well as reading up on the basic legal structures to isolate the importance of different legal document types. 

On the programmatic side, one of the biggest issues I had to resolve was how to pick up court case citations. An example of a citation looks like this: "Pilch v. Ashcroft, 353 F.3d 585 (7th Cir.2003)." I am indebted to the folks working on the Free Law Project's Court Listener project for providing the citation parser necessary to pick these citations up (https://www.courtlistener.com/). 

What I was able to do with these citations is apply graph theory through the Python Networkx graph module to discover communities of court cases based on the number of shared citations. Below I include a few examples of how this works: 

<p align="center"> 
<img src="https://github.com/305kev/Capstone_Proposal/blob/master/images/discover_communities.png" width=75% height=75% />
 <br> Figure 8. Legal A.I. discovering communities networkx graph
</p>

By adjusting the network graph to only include nodes of court cases and the edges that connects them as the number of citations they share, I was able to discover new communities of court cases. These new communities allowed me to return a list of 3 to 5 of the most related cases by the number of shared citations for each search result. This allows the user to continue looking at similar cases, should they find that search result to be relevant. 

<p align="center"> 
<img src="https://github.com/305kev/Capstone_Proposal/blob/master/images/graph_with_weights.png" width=75% height=75% />
 <br> Figure 9. Legal A.I. Networkx Graph Recommender: discovering communities with weighted edges
</p>


## Future improvements
An ideal A.I.-powered legal search engine would be able to optimize the scoring function, taking in inputs from 3 broad categories: (1) The Query (from a database of queries, as part of query understanding), (2) The data (using a variety of networkx graphs to measure importance of documents, independent of the query), and (3) user ratings (of whether or not expert users found the search result relevant). A future model could leverage user ratings as labeled data to train, 
and improve performance on. 

Additionally, one major drawback to my analysis is that it's based on cases scraped going back about 25 years, which highly biases results that are more recent. Future work could focus on acquiring a larger amount of data, as there over 200,000 immigration cases logged in the U.S. Although this would improve the model's understanding of underlying relationships, 
the trade off is significant storage and performance costs that could be overcome with clustering tools such as Spark. 

Finally, model currently only takes in one of 3 major areas of the law: judicial opinions (case law). To improve recall (the percent of truly relevant results returned), the model would have to include legal documents from the legislative branch (statutory laws; e.g. The Immigration and Nationality Act of 1952, or The Civil Rights Act 1964), and from the executive branch (Code of Federal Regulations -- C.F.R; rules that all federal agencies create to carry out legislative statues).  






