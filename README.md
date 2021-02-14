# Imperium

## Inspiration
The past year's events have made it even more pressing for our society to ensure the implementation inclusive practices and accessibility. The project stems from the sudden transition to online learning which disproportionally impacted students with disabilities
As ASL is note a compulsory language in elementary school, multiple students find themselves incapable of interacting with their peers even in later years of their life.  Furthermore, About 72% of hard of hearing employees have experience 'Audism' and 1 in 4 employees have reportedly left their job due to a non-inclusive environment.
Amplify/Handz aims to bridge the gap between ASL speakers and non ASL speakers by converting real time audio to ASL.
## What it does
The user enters an audio transcript --> Web Speech-to-Text API for converting audio to text --> Each word is linked with a unique ASL video --> The videos are put together to allow complete sentences to be converted from traditional speech to ASL.
## How we built it
#Scraping and pre-processing:
-- The scraping is done using selenium
-- In this step, the website handspeak.com is scraped for word, associated ASL clip.
--A Key-Value database is built storing the word and clip URL.
--BERT is used to pre-compute the embeddings of the dictionary word entries.
--This is then stored on a custom similarity database, backed by FAISS.
#Frontend:
video captured in frontend.
Audio track separated.
Web Speech-to-Text API for converting audio to text. (Capturing statements)
Statements send to backend as JSON via POST request.
#Backend:
Server receives it and puts in a processing queue.
Server spawns independent workers. The workers fetch entries from the processing queue, and processes them parallelly.
REST endpoint is built using Flask.
each worker:
takes the statement.
uses BERT (A Transformer based Language model by Google Research) and Facebook Research’s FAISS (A similarity search database) to break the statement into a set of optimal phrases.
optimal phrase is defined as a word, or collection of word which is present in our ASL dictionary OR it’s synonym is present in our ASL dictionary.
A novel greedy algorithm based on Spectral Clustering and Semantic Search using FAISS is used to do break the statement into minimal number of optimal phrases.
Another FAISS database is used to perform semantic search on the scraped database, to find the closest matching video link for the generated optimal phrase.
The worker returns the video link, which is stored on a heap (to maintain the order of the parallelly processed data).
Finally the frontend keeps on querying a REST end point, which returns the list of video links back (in order), which is then displayed one by one in order in a video container
## What's next for Imperium
The two marketing strategies:
--We hope to include Amplify/Handz as a critical tool for elementary school education which allows young students to learn ASL as a part of their traditional school experience.
--As a tool for non-ASL speakers to comfortably carry out a conversation with ASL speakers and reduce unintended Audism in the workplace.
