import sqlite3
import time
import re
import os
import getpass

# Global variables for database connection and cursor
connection = None
cursor = None

def connect(path):
    """
    Function to connect to the SQLite database.
    It takes a path to the database file.

    Arguments:
    path (str): The path to the SQLite database file.

    Returns: None
    """
    global connection, cursor

    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(' PRAGMA foreign_keys=ON; ')
    connection.commit()
    return

def clear():
    """
    Function to clear the console.
    It uses the 'cls' command for Windows and 'clear' for other operating systems.

    Arguments: None

    Returns: None
    """
    os.system('cls' if os.name=='nt' else 'clear')

def landing_page():
    """
    Main login page function.
    It provides options for the user to login, sign up or exit.

    Arguments: None

    Returns:
    output (int or function): 0 if the user chooses to exit, otherwise calls the login or signup page function.
    """
    
    clear()
    print('      TWEETBOOK.PY')
    print('************************')
    print('To login, press L')
    print('To sign up, press S')
    print('To exit, press X')
    print('************************')
    
    landing_input = input('Input:').lower()
    clear()
    output = 0

    if landing_input == "l":
        output = login_page()
         # This is in the case that there is no user with the matching usr and pwd values
        while output == None:
            clear()
            print('Your user ID and/or password is not correct:')
            output = login_page()
            
        # After logging in, show tweets page    
        output = tweet_page(output[0])
    elif landing_input == "s":
        return signup_page()
    elif landing_input == "x":
        output = 0
    else:
        input('Unrecognized input, press any key to try again')
        return landing_page()
    return output

def login_page():
    """
    Function for login page.
    It asks for user ID and password and checks them against the database.

    Arguments: None

    Returns:
    output (tuple): A tuple containing the user ID and password if they are found in the database, None otherwise.
    """

    global connection,cursor
    usr = input('Enter your user ID:')
    pwd = getpass.getpass('Enter your password: ')
    cursor.execute('SELECT usr,pwd FROM users WHERE usr=? AND pwd=?',(usr,pwd))
    output = cursor.fetchone()
    connection.commit()
    return output

def signup_page():
    """
    Function for signup page.
    It asks for personal information and inserts a new user into the database.

    Arguments: None

    Returns:
    landing_page (function): Calls the landing_page function after successfully signing up a new user.
    """

    global connection,cursor
    print('Firstly, we would like some personal information.')
    name = input('Please enter your name:')
    email = input('Please enter your email:')
    city = input('Please enter your city:')
    timezone = input('Please enter your timezone:')
    pwd = input('Please enter your password:')
    cursor.execute('SELECT MAX(usr) FROM users')
    usr = cursor.fetchone()[0] + 1
    cursor.execute('INSERT INTO users(usr,pwd,name,email,city,timezone) VALUES (?,?,?,?,?,?)',(usr,pwd,name,email,city,timezone))
    connection.commit()
    return landing_page()

def tweet_page(usr):
    """
    Main page function after user login.
    It provides multiple functionalities for the user to interact with tweets.

    Arguments:
    usr (str): The user ID of the logged-in user.

    Returns:
    data (list): A list of dictionaries containing the tweets displayed on the page.
    """
    global connection,cursor

    # Initialize page number and user input
    page_num = 1
    tweet_input = ''

    while (tweet_input != 'x'):
        clear()
        print('      TWEETBOOK.PY')
        print('************************')

        # Calculate the offset for pagination
        offset = (page_num-1)*5

        # Execute the SQL query to fetch tweets from followed users and retweets
        cursor.execute("""
            SELECT tweets.*
            FROM tweets
            JOIN follows ON follows.flwee = tweets.writer
            WHERE follows.flwer = ?
            UNION
            SELECT tweets.*
            FROM tweets
            JOIN retweets ON retweets.tid = tweets.tid
            JOIN follows ON follows.flwee = retweets.usr
            WHERE follows.flwer = ?
            ORDER BY tweets.tdate DESC
            LIMIT 5 OFFSET ?""", (usr,usr,offset))
        connection.commit()

        # Fetch the results and convert them into a list of dictionaries
        desc = cursor.description
        column_names = [col[0] for col in desc]
        data = [dict(zip(column_names, row))  
            for row in cursor.fetchall()]

        # Print the results
        for i, row in enumerate(data, start=1):
            row['num'] = i

        for row in data:
            print(row['num'], ": ", row['text'])
        
        print("P: Previous <--  --> N: Next")
        print('************************')
        print("To perform an action on a tweet, enter a tweet number (1-5)")
        print("To compose a tweet, press C")
        print("To pay respects to your followers, press F")
        print("To search for users, press U")
        print("To search for Tweets, press T")
        print("To log out, press X")
        tweet_input = input('Input:').lower()

        # Perform an action based on the user's input
        if (tweet_input == 'n'):
            page_num += 1
        elif (tweet_input == 'p'):
            page_num -= 1
        elif (tweet_input == 'c'):
            compose_tweet(usr,None)
        elif (tweet_input == 'f'):
            followers_page(usr)
        elif (tweet_input == 'u'):
            search_users(usr)
        elif (tweet_input == 't'):
            search_tweets(usr)
        elif (tweet_input.isdigit() and int(tweet_input)<=len(data)):
            tweet_action(data[int(tweet_input)-1].get('tid'),usr)
    return data

def tweet_action(tid,usr):
    """
    Function to perform actions on a tweet.
    It provides options for the user to go back, reply to or retweet a tweet.

    Arguments:
    tid (str): The tweet ID of the selected tweet.
    usr (str): The user ID of the logged-in user.

    Returns: None
    """
    global connection, cursor

    # Clear the console
    clear()

    # Execute the SQL query to get the number of retweets
    cursor.execute('SELECT COUNT(*) FROM retweets r1 WHERE r1.tid = ?',(tid,))
    rt_stats = cursor.fetchone()[0]

    # Execute the SQL query to get the number of replies
    cursor.execute('SELECT COUNT(*) FROM tweets t1 WHERE t1.replyto = ?',(tid,))
    rp_stats = cursor.fetchone()[0]
    
    while (True):
        # Print the tweet stats
        print('This tweet has',rt_stats,'retweets and',rp_stats,'replies')

        # Commit any changes to the database
        connection.commit()

        print("Hit X to go back, R to reply and RT to retweet")
        stat_input = input('Input:').lower()

        # Perform an action based on the user's input
        if (stat_input == 'x'):
            break
        elif (stat_input == 'r'):
            compose_tweet(usr,tid)
            clear()
        elif (stat_input == 'rt'):
            clear()
            input('Retweeted tweet! Press any key to continue')
            clear()

            # Get the current date
            rdate = time.strftime("%Y-%m-%d")

            # Execute the SQL query to insert a new retweet
            cursor.execute('REPLACE INTO retweets(usr,tid,rdate) VALUES (?,?,?)',(usr,tid,rdate))

            # Commit any changes to the database
            connection.commit()
        else:
            clear()
            input("Please Enter from the given options, press any key to continue")
            clear()
    return

def compose_tweet(usr,replyto):
    """
    Function to compose a tweet or reply to a tweet.

    Arguments:
    usr (str): The user ID of the logged-in user.
    replyto (str): The tweet ID of the tweet to reply to. If None, a new tweet is composed.

    Returns: None
    """
    # Clear the console
    clear()

    # Get the text of the tweet or reply
    if replyto == None:
        text = input("Write out your tweet:")
    else:
        text = input("Write out your reply:")

    # Find all hashtags in the text
    hashtags = re.findall("[#]\w+", text)

    # Get a new tweet ID
    cursor.execute('SELECT MAX(tid) FROM tweets')
    tid = cursor.fetchone()[0] + 1

    # Get the current date
    tdate = time.strftime("%Y-%m-%d")

    # Insert the new tweet or reply into the database
    cursor.execute("INSERT INTO tweets(tid,writer,tdate,text,replyto) VALUES (?,?,?,?,?)",(tid,usr,tdate,text,replyto))
    
    # Handle the hashtags
    for i in hashtags:
        term = i[1:]
        print(term)

        # Insert the hashtag into the database
        cursor.execute('REPLACE INTO hashtags(term) VALUES (?)',(term,))

        # Insert the mention into the database
        cursor.execute('INSERT INTO mentions(tid,term) VALUES(?,?)',(tid,term,))       

    # Commit any changes to the database
    connection.commit()
    return

def followers_page(usr):
    """
    Function to display the followers page.
    It provides options for the user to perform actions on a follower or exit the page.

    Arguments:
    usr (str): The user ID of the logged-in user.

    Returns: None
    """
    global connection,cursor
    flwer_input = ''

    while (flwer_input != 'x'):
        # Clear the console
        clear()

        print('      TWEETBOOK.PY')
        print('************************')

        # Get the followers of the user
        cursor.execute("""
            SELECT u1.*
            FROM follows f1, users u1
            WHERE f1.flwee = ?
            AND f1.flwer = u1.usr""", (usr,))

        # Commit any changes to the database
        connection.commit()
        
        # Get the column names and the data
        desc = cursor.description
        column_names = [col[0] for col in desc]
        data = [dict(zip(column_names, row))  
            for row in cursor.fetchall()]

        # Add a number to each row
        for i, row in enumerate(data, start=1):
            row['num'] = i

        # Print the followers
        for row in data:
            print(row['num'], ": ", row['name'] ,"- ", row['usr'])

        print('************************')
        print("To perform an action on a follower, enter a number corresponding to that follower")
        print("To exit, press X")

        # Get the user's input
        flwer_input = input('Input:').lower()

        # Perform an action based on the user's input
        if (flwer_input.isdigit() and int(flwer_input)<=len(data)):
            flwer_action(data[int(flwer_input)-1].get('usr'),usr)
    return

def flwer_action(flwer,usr):
    """
    Function to perform actions on a follower.
    It provides options for the user to go back, follow the follower, or navigate through the follower's tweets.

    Arguments:
    flwer (str): The user ID of the selected follower.
    usr (str): The user ID of the logged-in user.

    Returns: None
    """
    global connection, cursor
    page_num = 1

    # Get the number of tweets from the follower
    cursor.execute('SELECT COUNT(*) FROM tweets WHERE writer = ?',(flwer,))
    tweet_count = cursor.fetchone()[0]

    # Get the number of users the follower is following
    cursor.execute('SELECT COUNT(*) FROM follows WHERE flwer = ?',(flwer,))
    following_count = cursor.fetchone()[0]

    # Get the number of followers of the follower
    cursor.execute('SELECT COUNT(*) FROM follows WHERE flwee = ?',(flwer,))
    follower_count = cursor.fetchone()[0]

    # Get the name of the follower
    cursor.execute('SELECT name FROM users WHERE usr = ?',(flwer,))
    follower_name = cursor.fetchone()[0]

    fa_input = ''

    while (fa_input != 'x'):
        # Clear the console
        clear()

        print('      TWEETBOOK.PY')
        print('************************')
        print("User ID: ", flwer,' Username: ', follower_name, ' Tweets: ', tweet_count, ' Following: ', following_count, ' Followers: ', follower_count)

        offset = (page_num - 1)*3
        cursor.execute("""
            SELECT text
            FROM tweets
            WHERE writer = ?
            ORDER BY tdate DESC
            LIMIT 3 OFFSET ?""", (flwer,offset))

        # Commit any changes to the database
        connection.commit()
        
        # Get the column names and the data
        desc = cursor.description
        column_names = [col[0] for col in desc]
        data = [dict(zip(column_names, row))  
            for row in cursor.fetchall()]

        # Add a number to each row
        for i, row in enumerate(data, start=1):
            row['num'] = i

        # Print the tweets
        for row in data:
            print(row['num'], ": ", row['text'])

        print("P: Previous <--  --> N: Next")
        print('************************')
        print("Hit X to go back or F to follow")

        # Get the user's input
        fa_input = input('Input:').lower()

        # Perform an action based on the user's input
        if (fa_input == 'f'):
            start_date = time.strftime("%Y-%m-%d")
            cursor.execute('REPLACE INTO follows(flwer,flwee,start_date) VALUES (?,?,?)',(usr,flwer,start_date))

            # Commit any changes to the database
            connection.commit()

            input("You are now following this user, please hit any key to continue")
        elif (fa_input == 'n'):
            page_num += 1
        elif (fa_input == 'p'):
            page_num -= 1

    # Commit any changes to the database
    connection.commit()
    return

def search_tweets(usr):
    """
    Function to search tweets based on keywords.
    It provides options for the user to go back, select a tweet, or navigate through the search results.

    Arguments:
    usr (str): The user ID of the logged-in user.

    Returns: None
    """
    global connection, cursor

    # Get the keywords from the user
    key_word = input("Enter a keyword or multiple keywords (separated by a space): ").split()
    page_num = 1

    while key_word:
        # Initialize the list of tweets
        tweetlist = []

        # For each keyword
        for i in key_word:
            offset = (page_num-1)*5

            # If the keyword is a hashtag
            if re.match(r'^#', i):
                cursor.execute("""
                    SELECT t1.*
                    FROM tweets t1, mentions m1
                    WHERE m1.term LIKE ? 
                    AND m1.tid = t1.tid
                    ORDER BY tdate DESC
                    LIMIT 5 OFFSET ?;
                """, (i[1:], offset))
            else:  
                cursor.execute("""
                    SELECT * FROM Tweets 
                    WHERE text LIKE ? ORDER BY tdate DESC LIMIT 10 OFFSET ?;""",
                    ('%'+i+'%', offset))

            # Fetch the results
            result = cursor.fetchall()

            # Remove duplicates and add the results to the list of tweets
            tweetlist = result + list(set(tweetlist)-set(result))

        # Clear the console
        clear()

        print('      TWEETBOOK.PY')
        print('************************')

        # Print the tweets
        digit=1
        for text in tweetlist:
            print(digit , ": " , str(text[3]) , "- " , str(text[0]))
            digit+=1;

        print("P: Previous <--  --> N: Next")
        print('************************')
        print("Hit X to go back or S to Select Tweet")

        # Get the user's input
        fa_input = input('Input:').lower()
        
        # Perform an action based on the user's input
        if (fa_input == 's'):
            tid=input("Enter Tweet Id you want to view: ")
            tweet_action(tid,usr)
        elif (fa_input == 'n'):
            page_num += 1
        elif (fa_input == 'p'):
            if page_num != 1:
                page_num -= 1
            else:
                print("Cannot go back")
        elif (fa_input == 'x'):
            return 
    return

def search_users(usr):
    """
    Function to search users based on a keyword.
    It provides options for the user to go back, select a user, or navigate through the search results.

    Arguments:
    usr (str): The user ID of the logged-in user.

    Returns: None
    """
    # Get the keyword from the user
    keyword = input("Enter Search Keyword: ").lower()
    search_user_input = ''
    page_num = 1

    while (search_user_input != 'x'):
        clear()
        print('      TWEETBOOK.PY')
        print('************************')

        # Calculate the offset for pagination
        offset = (page_num-1)*5

        # Execute the SQL query to search users by name or city
        cursor.execute('''
            SELECT *
            FROM users
            WHERE LOWER(name) LIKE ? OR LOWER(city) LIKE ?
            ORDER BY
            CASE
                WHEN LOWER(name) LIKE ? THEN 0
                ELSE 1
            END,
            LENGTH(name) ASC, 
            LENGTH(city) ASC
            LIMIT 5 OFFSET ?''', ('%'+keyword+'%', '%'+keyword+'%', '%'+keyword+'%', offset))
        connection.commit()

        # Fetch the results and convert them into a list of dictionaries
        desc = cursor.description
        column_names = [col[0] for col in desc]
        data = [dict(zip(column_names, row))  
            for row in cursor.fetchall()]

        # Print the results
        for i, row in enumerate(data, start=1):
            row['num'] = i

        for row in data:
            print(row['num'], ": ", row['name'], " - ", row['usr'])
        
        print("P: Previous <--  --> N: Next")
        print('************************')
        print("To perform an action on a user, enter a number corresponding to that follower")
        print('To exit, press X')
        search_user_input = input("Input: ").lower()

        # Perform an action based on the user's input
        if (search_user_input.isdigit() and int(search_user_input)<=len(data)):
            flwer_action(data[int(search_user_input)-1].get('usr'),usr)   
        elif (search_user_input == 'n'):
            page_num += 1
        elif (search_user_input == 'p'):
            page_num -= 1     

    return

def main():
    """
    Main function to run the application.
    It asks for the database name, connects to it, and then runs the landing page in a loop until the user decides to exit.

    Arguments: None

    Returns: None
    """
    global connection, cursor

    # Get the database name from the user
    filename = input('Enter your database name (with the .db extension):')

    # Construct the path to the database file
    path="./"+filename

    # Connect to the database
    connect(path)

    # Run the landing page in a loop
    i= True
    while i:
        ans = landing_page()
        if ans == 0:
           i=False

    # Commit any changes and close the connection to the database
    connection.commit()
    connection.close()

    return

if __name__ == "__main__":
    main()
