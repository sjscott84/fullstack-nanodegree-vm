#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM matches")
    c.execute("UPDATE players SET player_losses = %s,\
        player_wins = %s", (0,0))
    conn.commit()
    conn.close()


def deletePlayers():
    """Remove all the player records from the database."""
    conn = connect()
    c = conn.cursor()
    c.execute("DELETE FROM players")
    conn.commit()
    conn.close()


def countPlayers():
    """Returns the number of players currently registered."""
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT count (player_id) FROM players")
    count = c.fetchone()
    conn.commit()
    conn.close()
    return count[0]


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    conn = connect()
    c = conn.cursor()
    c.execute("INSERT into players values (default,%s,0,0)",\
        [name])
    conn.commit()
    conn.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """

    conn = connect()
    c = conn.cursor()
    c.execute("SELECT * from players ORDER By player_wins desc")
    data = c.fetchall()
    conn.commit()
    conn.close()
    l = []
    for row in data:
        l.append((row[0], row[1], row[2], row[2] + row[3]))
    return l


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT player_wins FROM players where player_id = %s",\
        [winner])
    update_wins = c.fetchone()[0] + 1
    c.execute("SELECT player_losses FROM players where player_id = %s",\
        [loser])
    update_losses = c.fetchone()[0] + 1
    c.execute("INSERT into matches VALUES (default, %s, %s, %s)",\
        (winner, loser, winner))
    c.execute("UPDATE players SET player_wins = %s WHERE player_id = %s",\
        (update_wins, winner))
    c.execute("UPDATE players SET player_losses = %s WHERE player_id = %s",\
        (update_losses, loser))
    conn.commit()
    conn.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT * from players ORDER By player_wins desc")
    data = c.fetchall()
    conn.commit()
    conn.close()
    l = []
    count = 0
    while count < len(data):
        l.append((data[count][0], data[count][1],
            data[count+1][0], data[count+1][1]))
        count = count + 2
    return l


