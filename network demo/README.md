# Data Structures

I use networks (instead of trees) in my project. I construct these networks in two different ways, and I only use one of them due to a bug with Jinja 2 (or pyvis; I'm not really sure).

The first network is a co-occurrence network of named entities. The network is created by first tokenizing the words of a transcript, finding a subset of named entities in the transcript (I leave out entities like Ordinal and Cardinal), and finding all of the entities that appear within 7 words of one another. This forms a weighted undirected network, where the weights are the number of times that entities co-occur with one another. 

Since these networks can get very busy, I used networkx's pagerank algorithm to get only the most central nodes from this co-occurrence network. The less connected nodes aren't as interesting for the purposes of getting summary information about a video, so there is no point in including them. This isn't a typical application of pagerank since the graph is undirected, but getting the most connected nodes is still useful for my purposes. 

I wanted a visualization of words that are close together because I only provide ChatGPT with a 2000 word window of the video transcript, so relationships between named entities that are within 7 words of one another will likely fall within the same chunk and be answerable.

A json of a sample network is stored in `./co_occurrence.json`. A pyvis visualization of the network is stored in `./co_occurrence_graph.html`.

I wont discuss the other clustering network I made because I didn't use it in the final flask app.

Rendered Co-occurrence html file screenshot:

<img width="585" alt="Screen Shot 2023-04-21 at 8 13 53 PM" src="https://user-images.githubusercontent.com/60138157/233751315-ea82855d-7cb6-4710-8e5b-c344cb085a0b.png">

Parsed json file with network nodes/edges (nodes is minimized so you can see all of the keys):

<img width="442" alt="Screen Shot 2023-04-21 at 8 16 35 PM" src="https://user-images.githubusercontent.com/60138157/233751443-b5e34cdd-6ae9-4812-b569-8ced9d29478e.png">


