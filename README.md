This repository is a backup of a twitter CLI clone, this was made for a university project.

Collaborators included in design docs

How to use MongoDB:
1. Run `./setup.sh <port number> <JSON path>` on the command line where the port number is used to connect to the mongoDB server
2. In a separate terminal window run `python3 tweetbook.py <port number>` where the port number is the same port number from the 1st step to run the queries you run

Closing MongoDB Connection
- To shutdown mongoDB connection to server or restart it, run this command:
    `./reset.sh <port number>`
