-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- Ensure you create these tables in the database by running \i tournament.sql
-- once connected to the tournment database

-- Creates a table to hold all the players
CREATE TABLE Players (
    id serial primary key,
    name text
);

-- Creates a table to hold all of the matches
CREATE TABLE Matches (
    match_num serial primary key,
    winner serial references Players,
    loser serial references Players
);

CREATE VIEW player_standings as
    SELECT id, name, COUNT (CASE WHEN id = winner THEN winner END) as wins,
    COUNT (CASE WHEN id = winner OR id = loser THEN match_num END) as matches_played
    FROM players LEFT JOIN matches ON id = winner or id = loser GROUP BY id;
