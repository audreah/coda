use coda_db;
 
-- drop tables
drop table if exists coda_playlist;
drop table if exists coda_song;
drop table if exists coda_album;
drop table if exists coda_artist;
drop table if exists coda_friend;
drop table if exists coda_user;
 
-- create tables
CREATE TABLE coda_user (
   user_id int auto_increment not null primary key,
   user_name varchar(50)
)
ENGINE=InnoDB;
 
CREATE TABLE coda_friend (
   friend_one int,
   friend_two int,
   INDEX(friend_one),
   INDEX(friend_two),
   foreign key (friend_one) references coda_user(user_id)
       on update cascade
       on delete cascade,
   foreign key (friend_two) references coda_user(user_id)
       on update cascade
       on delete cascade
)
ENGINE=InnoDB;
 
CREATE TABLE coda_artist (
   artist_id int auto_increment not null primary key,
   artist_name varchar(50),
)
ENGINE=InnoDB;
 
CREATE TABLE coda_album (
   album_id int auto_increment not null primary key,
   album_title varchar(50),
   artist_id int,
   release_year char(4),
   INDEX(artist_id),
   foreign key (artist_id) references coda_artist(artist_id)
       on update restrict
       on delete restrict
)
ENGINE=InnoDB;
 
CREATE TABLE coda_song (
   song_id int auto_increment not null primary key,
   song_title varchar(50),
   genre varchar(50),
   album_id int,
   added_by int,
   INDEX(album_id),
   INDEX(added_by),
   foreign key (album_id) references coda_album(album_id)
       on update restrict
       on delete restrict,
   foreign key (added_by) references coda_user(user_id)
       on update restrict
       on delete set null
)
ENGINE=InnoDB;
 
CREATE TABLE coda_playlist (
   playlist_id int auto_increment not null primary key,
   playlist_name varchar(50),
   playlist_genre varchar(50),
   created_by int,
   INDEX(created_by),
   foreign key (created_by) references coda_user(user_id)
       on update restrict
       on delete cascade
)
ENGINE=InnoDB;
 
-- intermediate table (similar to wmdb’s credit table)
-- indicating which songs are on which playlists
CREATE TABLE coda_playlist_songs (
   playlist_id int not null,
   song_id int not null,
   primary key (playlist_id, song_id),
   foreign key (playlist_id) references coda_playlist(playlist_id)
       on update cascade
       on delete cascade,
    foreign key (song_id) references coda_song(song_id)
       on update cascade
       on delete cascade
)
ENGINE=InnoDB;
