#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import praw, pdb, re, os, time

PRAW_BOT_SITE = "you_forgot_the_slash"
REPLIED_FILE = "replied.txt"
SUBREDDITS = "karmacourt"

reddit = praw.Reddit(PRAW_BOT_SITE)
subreddit = reddit.subreddit(SUBREDDITS)

with open(REPLIED_FILE, "r") as f:  # Do not use 'w+', it empties the file
    data = f.read()
    replied = [i for i in data.split("\n") if i]  # Split lines and remove empty entries
    print(replied)
    print("====================================================")

username_pattern = re.compile("u\/(?:[a-z]|[A-Z]|[0-9]|-|_){3,20}", re.IGNORECASE) # Match Reddit username pattern limitations
for submission in subreddit.stream.submissions():
    if submission.id not in replied:
        title_matches = username_pattern.findall(submission.title)
        text_matches = username_pattern.findall(submission.selftext)
        if (title_matches or text_matches) and submission.id not in replied:
            reply = ""
            
            # Title
            plu_sing_slash = "a slash" if len(title_matches)==1 else "some slashes"
            end = ""
            if len(title_matches) == 1:  # Singular
                end = "'/{0}' instead of '{0},'"
            elif len(title_matches) > 1:  # Use 'and' if more than 1 instance
                for i in range( len(title_matches)-1 ):
                    end = "'/{{{{{0}}}}}' instead of '{{{{{0}}}}},'".format(i) * (len(title_matches)-1)
                argnums = [i for i in range(len(title_matches))]
                end += "and '/{{{{{0}}}}}' instead of '{{{{{0}}}}}'".format( len(title_matches)-1 )
                end = end.format(*argnums)
            if title_matches:
                end = end.format(*title_matches)
                reply += "You seem to have forgotten {} in your title, did you mean {}?".format(plu_sing_slash, end)
            
            # Selftext
            if reply:  # Use 'more', 'also'
                start = "\n\nAlso, y"
                plu_sing_slash = "one more slash" if len(text_matches)==1 else "some more slashes"
            elif not reply:
                start = "Y"
                plu_sing_slash = "a slash" if len(text_matches)==1 else "some slashes"
            end = ""  # Clear 'end' for Selftext processing
            
            if len(text_matches) == 1:  # Singular
                end = "'/{0}' instead of '{0},'"
            elif len(text_matches) > 1:  # Use 'and' if more than 1 instance
                for i in range( len(text_matches)-1 ):
                    end = "'/{{{{{0}}}}}' instead of '{{{{{0}}}}},'".format(i) * (len(text_matches)-1)
                argnums = [i for i in range(len(text_matches))]
                end += "and '/{{{{{0}}}}}' instead of '{{{{{0}}}}}'".format( len(text_matches)-1 )
                end = end.format(*argnums)
            if text_matches:
                end = end.format(*text_matches)
                reply += "{}ou appear to have omitted {} in your post-text, did you mean {}?".format(start, plu_sing_slash, end)
            
            reply += "\n\n---\n\n*Due to the nature of this subreddit, I am assuming that you intend to summon the user(s) mentioned in your post. \
To summon a user, you must prefix another '/' before their username, otherwise it will only provide a link without notifying them.*\
\n\n---\n\n*(Boop, boop I am a bot, this action was performed automatically. \
Please [contact the moderators of this subreddit](/message/compose/?to=/r/{}) if you have any questions or concerns.)*".format(submission.subreddit)
            
            counter = 0
            while counter <= 2:
                try:
                    submission.reply( reply )
                    replied.append(submission.id)
                    with open(REPLIED_FILE, "a+") as f:
                        f.write( str(submission.id) + "\n" )
                    
                    print("ID: ", submission.id)
                    print("Title: ", submission.title)
                    print("Body: ", submission.selftext)
                    print()
                    
                    print("Title matches:  ", title_matches)
                    print("Selftext matches:  ", text_matches)
                    #print("\nReply:\n", reply)
                    print("====================================================")
                    break
                except praw.exceptions.APIException:
                    counter += 1
                    print("Attempt : {} : failed".format(counter))
                    time.sleep(300)  # Wait 5 minutes