import pymongo
import sys
import os
from datetime import datetime, timezone 

client = pymongo.MongoClient('mongodb://localhost:{}'.format(sys.argv[1]))
db = client["291db"]
infoCollection = db["tweet_info"]

def clear():
    """
    Clears the console screen.
    """
    os.system('cls' if os.name=='nt' else 'clear')

def landing_page(args):
    """
    Displays the landing page and handles user input for different actions.

    Args:
        args (list): Command-line arguments passed to the script.

    Returns:
        list: The updated list of command-line arguments.
    """
    landing_input = ''

    # Loop to display the landing page until the user chooses to exit
    while (landing_input != 'x'):
        clear()

        # Displaying the main menu options
        print('      TWEETBOOK.PY')
        print('************************')
        print('To search for tweets, press T')
        print('To search for users, press U')
        print('To list top n tweets, type LT')
        print('To list top n users, press LU')
        print('To compose a tweet, press C')
        print('To exit, press X')
        print('************************')
        landing_input = input('Input:').lower()

        # Handling user input based on their choice
        if (landing_input == 't'):
            search_tweets()
        elif (landing_input == 'u'):
            search_users()
        elif (landing_input == 'lt'):
            list_tweets()
        elif (landing_input == 'lu'):
            list_users()
        elif (landing_input == 'c'):
            compose_tweets()
        elif (landing_input == 'x'):
            return args

def search_tweets():
    """
    Searches for tweets based on user input.

    Returns:
        None
    """
    while True:
        clear()
        print('')
        print('Please enter keywords to search for tweets (separate by spaces), or type "x" to return:')
        print('')
        user_input = input('Input: ').strip()
        if user_input.lower() == 'x':
            break

        keywords = user_input.split()
        if not keywords:
            continue

        # Building a query for MongoDB based on user input keywords
        regex_query = [{"content": {"$regex": keyword, "$options": "i"}} for keyword in keywords]
        query = {"$and": regex_query}

        # Searching for tweets in the database based on the query
        found_tweets = infoCollection.find(query)
        tweet_data = {i: tweet for i, tweet in enumerate(found_tweets, start=1)}

        if not tweet_data:
            print("No tweets found with the given keywords.")
            input('Press any key to continue...')
            continue

        # Displaying the found tweets with basic information
        for index, tweet in tweet_data.items():
            print(f"TWEET {index}:")
            print("ID:", tweet['id'], "| Date:", tweet['date'], "| Content:", tweet['content'], "| Username:", tweet['user']['username'])
            print('')

        # Prompting the user to select a tweet for detailed information
        print('Enter a tweet number to see all fields, or press "x" to return to search:')
        selection = input('Input: ').strip()
        if selection.lower() == 'x':
            continue
        if selection.isdigit() and int(selection) in tweet_data:
            # Displaying detailed information for the selected tweet
            selected_tweet = tweet_data[int(selection)]
            clear()
            for field, value in selected_tweet.items():
                print(f"{field}: {value}")
            input('Press any key to continue...')
        else:
            print("Invalid selection. Please try again.")
            input('Press any key to continue...')

def search_users(): 
    """
    Searches for users based on user input.

    Returns:
        None
    """
    disp_u_input = ''
    while (disp_u_input != "x"):
        clear()
        print('')
        print('Please enter a keyword to search for users')
        print('')
        su_input = input("Input:")

        # This is the query to find users that match display name and location with case insensitivity
        query = {
            "$or": [
                {"user.displayname": {"$regex": r'\b' + su_input + r'\b', "$options": "i"}},
                {"user.location": {"$regex": r'\b' + su_input + r'\b', "$options": "i"}},
            ]
        }

        found_users = infoCollection.find(query)
        # Removing duplicates:
        final_users = {user["user"]["username"]: user["user"] for user in found_users}.values()
        
        # Data stored in dictionary with indexes for selection
        # formatted as: {index , user}
        data = {}
        i = 0
        clear()
        print('')
        for user in final_users:
            data[i] = user
            print("USER", (i+1), ":")
            print('')
            print("username:", user["username"], "| display name:", user["displayname"], "| location:", "N/A" if user["location"] is None else user["location"])
            print('')
            print('')
            i += 1
        print('Enter a user number to see all fields of the user')
        print('Otherwise press x to return')
        disp_u_input = input('Input:')
        if (disp_u_input.isdigit() and int(disp_u_input) < (i+1)):
            clear()
            for field in data[int(disp_u_input)-1]:
                print("*", field, ": ", data[int(disp_u_input)-1][field])
            print('')
            input('Press any key to continue')
        elif (disp_u_input == 'x'):
            return

def list_tweets():
    """
    Lists the top n tweets based on user input.

    Returns:
        None
    """
    list_input = ""
    while (list_input != 'x'):
        clear()
        print('')
        print('Please enter the number of tweets you would like to see')
        print('')
        print('Otherwise press x to return to the main screen')
        list_input = input('Input:').lower()
        if (list_input == 'x'):
            return
        elif list_input.isdigit():
            field_input = ""
            while (field_input !='x'):
                clear()
                print('')
                print('Please input the metric to sort the tweets (1-3)')
                print('1 | Retweet Count')
                print('2 | Like Count')
                print('3 | Quote Count')
                print('Otherwise press x to return')
                field_input = input('Input:')
                if (field_input == "1"):
                    display_top_tweets("retweetCount", list_input)
                elif (field_input == "2"):
                    display_top_tweets("likeCount", list_input)
                elif (field_input == "3"):
                    display_top_tweets("quoteCount", list_input)
                elif (field_input == 'x'):
                    return

def display_top_tweets(criteria, n):
    """
    Displays the top tweets based on the given criteria and the number of tweets to display.

    Args:
        criteria (str): The metric to sort the tweets by.
        n (str): The number of tweets to display.

    Returns:
        None
    """
    disp_tt_input = ''
    while (disp_tt_input != "x"):
        # Querying the database to get the top tweets based on the specified criteria and number
        toptweets = infoCollection.find({}).sort(criteria, pymongo.DESCENDING).limit(int(n))
        # Data stored in a dictionary with indexes for selection
        # formatted as: {index , tweet}
        data = {}
        i = 0
        clear()
        print('')
        for tweet in toptweets:
            data[i] = tweet
            print("TWEET", (i+1), ":")
            print("-----------------------------------------------------------------------")
            print(tweet['renderedContent'])
            print("-----------------------------------------------------------------------")
            # IGNORE BELOW, TEST PRINT
            # print(tweet['retweetCount'],tweet['likeCount'],tweet['quoteCount'],"id:" , tweet['id'] , "| date:", tweet['date'] , "| username:",tweet['user']['username'])
            print("id:", tweet['id'], "| date:", tweet['date'], "| username:", tweet['user']['username'])
            print('')
            print('')
            print('')
            i += 1
        print('Enter a tweet number to see all fields of the tweet')
        print('Otherwise press x to return')
        disp_tt_input = input('Input:')
        if (disp_tt_input.isdigit() and int(disp_tt_input) < (i+1)):
            clear()
            # Displaying detailed information for the selected tweet
            for field in data[int(disp_tt_input)-1]:
                print("*", field, ": ", data[int(disp_tt_input)-1][field])
            print('')
            input('Press any key to continue')
        elif (disp_tt_input == 'x'):
            return

def list_users():
    """
    Displays the top users based on the number of followers.

    Returns:
        None
    """
    list_input = ""
    while (list_input != 'x'):
        clear()
        print('')
        print('Please enter the number of top users you would like to see')
        print('')
        print('Otherwise press x to return to the main screen')
        list_input = input('Input:').lower()
        if (list_input == 'x'):
            return
        elif list_input.isdigit():
            # MongoDB aggregation pipeline to find top users based on followersCount
            pipeline = [
                {"$unwind": "$user"},  # Unwind the "user" array to work with individual tweets
                {"$group": {
                    "_id": "$user.username",
                    "maxFollowersCount": {"$max": "$user.followersCount"},
                    "displayname": {"$first": "$user.displayname"},
                    "full": {"$first": "$user"}
                }},
                {"$sort": {"maxFollowersCount": -1}},
                {"$limit": int(list_input)}
            ]

            # Execute the aggregation pipeline
            top_users = list(infoCollection.aggregate(pipeline))
            data = []
            i = 0
            clear()
            print('')
            for user in top_users:
                data.append(user)
                print("USER", (i+1), ":")
                print("-----------------------------------------------------------------------")
                print(f"Username: {user['_id']} | Display Name: {user['displayname']} | Follower Count: {user['maxFollowersCount']}")
                print('')
                print('')
                print('')
                i += 1
            print('Enter a user number to see all fields of the user')
            print('Otherwise press x to return')
            disp_tt_input = input('Input:')
            if (disp_tt_input.isdigit() and int(disp_tt_input) < (i+1)):
                clear()

                # Displaying detailed information for the selected user
                user = data[int(disp_tt_input)-1]
                print(f"{user['full']}")
                input("Press any key to return")

            elif (disp_tt_input == 'x'):
                return


def compose_tweets():
    """
    Composes a tweet and inserts it into the database.

    Returns:
        None
    """
    clear()
    print('')
    print('Please enter the text for your tweet')
    print('')
    tweet_input = input('Input:')

    # Converting time with timezone to ISO 8601 format without microseconds
    dtime = datetime.now(timezone.utc).replace(microsecond=0)
    dtimezone = dtime.astimezone().isoformat()

    tweet = {
        "url": None,
        "date": dtimezone,
        "content": tweet_input,
        "renderedContent": None,
        "id": None,
        "user": {
            "username": "291user",
            "displayname": None,
            "id": None,
            "description": None,
            "rawDescription": None,
            "descriptionUrls": [],
            "verified": None,
            "created": None,
            "followersCount": None,
            "friendsCount": None,
            "statusesCount": None,
            "favouritesCount": None,
            "listedCount": None,
            "mediaCount": None,
            "location": None,
            "protected": None,
            "linkUrl": None,
            "linkTcourl": None,
            "profileImageUrl": None,
            "profileBannerUrl": None,
            "url": None
        },
        "outlinks": None,
        "tcooutlinks": None,
        "replyCount": None,
        "retweetCount": None,
        "likeCount": None,
        "quoteCount": None,
        "conversationId": None,
        "lang": None,
        "source": None,
        "sourceUrl": None,
        "sourceLabel": None,
        "media": None,
        "retweetedTweet": None,
        "quotedTweet": None,
        "mentionedUsers": None,
    }

    # Insert the tweet into the database
    infoCollection.insert_one(tweet)
    clear()
    print('')
    print('Tweet successful!')
    print('')
    input('Press any key to return')
    return

def main():
    """
    The main entry point of the program.

    Returns:
        None
    """
    landing_page()
    return

if __name__ == "__main__":
    main()
