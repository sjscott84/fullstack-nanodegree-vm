-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- Creates a table to hold all the players
CREATE TABLE Players (
    player_id serial primary key,
    player_name text,
    player_wins smallint,
    player_losses smallint
);

--Creates a table to hold all of the matches
CREATE TABLE Matches (
    match_num serial,
    player_one serial,
    player_two serial,
    winner serial
);


