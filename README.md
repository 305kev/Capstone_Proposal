
# A.I. Legal Research Assistant

[__Fall 2017 Galvanize Data Science Immersive__](https://www.galvanize.com/austin)

An Investigation of legal research using the court cases scraped with Python's Beautiful Soup from FindLaw.com.

__Abstract:__ This project uses over 5,000 U.S. Supreme Court and U.S. Circuit Courts of Appeals' immigration cases. These were scraped using Python's Beautiful Soup from FindLaw.com on Amazon AMIs and S3. 

__Results:__ Built a fully functioning legal search engine able to take in free text queries and return relevant results based on cosine similarity built on Tf-IDF weights. Additionally, each result has 3 related court cases based on Networkx graph recommendations. 

See this work as a presentation in [Google Slides](https://docs.google.com/presentation/d/18PTXyDBYRlwHm7m53Z7BVN3Ix4OfCYLWLPpcTeVV6Is/edit?usp=sharing).

[See the video](https://www.youtube.com/watch?v=o5R0kOjtzwA&index=5&list=PLxtztEze-DRfCd2LY4IRytALcjpJQp0WC) of this talk.


## Motivation: 

Any U.S. citizen is entitled to legal representation under the law. The same is not true for non-citizens. In immigration court, over 80% of all defendants go unrepresented simply because they cannot afford a lawyer. Legal research stands among the highest costs for defendants. To illustrate, below are the national average of hourly rates for divorce attorneys: 

<p align="center"> 
<img src="https://github.com/305kev/Capstone_Proposal/blob/master/images/histogram_0.png" width=75% height=75% />

<br> Figure 1. Distribution of hourly rates for divorce attorneys, https://www.nolo.com/legal-encyclopedia/ctp/cost-of-divorce.html


## The Problem:
<br>

<img src="https://github.com/305kev/Capstone_Proposal/blob/master/images/pie.png" width="425"/><img src="https://github.com/305kev/Capstone_Proposal/blob/master/images/current_searches.png" width="425"/>

<br> Figure 2. Average time spent on legal research, http://bit.ly/1vfqzm3
<br> Figure 3. Current legal search queries, https://lscontent.westlaw.com/images/content/WLNT&CSearching.pdf 

<br>


## Potential Solution (Demo): 
This is where A.I. steps in. Although recent advances in machine learning have affected most major industries, the legal market is notably absent, with a few exceptions. ROSS A.I. is a startup company that has built a search engine built to optimize legal research; however they are solely focused on bankruptcy law. With this project, I intend to build upon their work and expand this ML powered search engine to new areas like immigration law. Below is an example of how it works: 

<p align="center"> 
<img src="https://github.com/305kev/Capstone_Proposal/blob/master/images/demo.gif" width=75% height=75% />
</p>

## The Process: 


<p align="center"> 
<img src="https://github.com/305kev/Capstone_Proposal/blob/master/images/pipeline.png" width=75% height=75% />
</p>

## The Challenge: 

One of the biggest hurdles to overcome is how to access all the relevant data. Using $15 per search engines like Westlaw and LexisNexis are not feasible, however convenient their aggregation of all relevant law types may be. Alternatively, it is possible to set up web-scrapers to access and store the data held piecemeal on many government websites and free legal resource sites like FindLaw.

In order to run a live demo by January 2018, my goal is to team up with a Galvanize web-development student to help build the front and backend of a website. The goal is to have a simple, yet useful search engine with features such as:

- Sorting by: Similarity/ Relevance, Date published, ranking of source law, etc. 
- Preview: See a clip of the document before clicking 
- Follow a search 
- Thumbs up/down (for feedback and potential recommender feature) 
- Categorical scale of positive or negative language


Next comes the data architecture problem. Where and how should I store the data? My plan is threefold: 
- (1) Will store live website database using NOSQL MongoDB and Flask 
- (2) One Githbub, I will store information as .txt files for ease of reproducement. 
- (3) On a AWS, I will store the MongoDB database as a cloud-based backup. 
 

The types of law pose a domain-knowledge challenge as well as a programmatic one. For the domain-based knowledge, I am working with several law students as well as reading up on the basic legal structures to isolate the importance of different legal document types. On the programmatic side, the task will be to classify the type of law: from case law (opinions), to statutory law (legislation), to (executive agency) regulation, etc. Next, I will implement a Natural Language Processing algorithm to parse through each type of legal document and identify similarity between text to return relevant information. Finally, I will use words associted with a positive and negative tone to score each document on a positive/negative scale to provide additional information to the user. 

Below is an example in python of how NLP works: 

<p align="center"> 
<img src="images/Example/nlp.png">
</p>


## Future improvements
An ideal A.I.-powered legal search engine would be able optimize the scoring function, taking in inputs from 3 broad categories: (1) The Query (from a database of queries, as part of query understanding), (2) The data (using a variety of networkx graphs to measure importance of documents, independent of the query), and (3) user ratings (of whether or not expert users found the search result relevant). A future model could leverage user ratings as labeled data to train, 
and improve performance on. 

Additionally, one major drawback to my analysis is that it's based on cases scraped going back about 25 years, which highly biases results that are more recent. Future work could focus on acquiring a larger amount of data, as there over 200,000 immigration cases logged in the U.S. Although this would improve the model's understanding of underlying relationships, 
the trade off is significant storage and performance costs that could be overcome with clustering tools such as Spark. 

Finally, model currently only takes in one of 3 major areas of the law: judicial opinions (case law). To improve recall (the percent of truly relevant results returned), the model would have to include legal documents from the legislative branch (statutory laws; e.g. The Immigration and Nationality Act of 1952, or The Civil Rights Act 1964), and from the executive branch (Code of Federal Regulations -- C.F.R; rules that all federal agencies create to carry out legislative statues).  






