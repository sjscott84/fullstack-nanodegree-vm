-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

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


