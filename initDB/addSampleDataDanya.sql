use coda_db;
 
insert into coda_user(user_name) values ('Danya');
 
insert into coda_artist(artist_name) values ('Bleachers');
insert into coda_artist(artist_name) values ('Lana Del Rey');
insert into coda_artist(artist_name) values ('Hozier');
insert into coda_artist(artist_name) values ('Joji');
insert into coda_artist(artist_name) values ('Rejjie Snow');
insert into coda_artist(artist_name) values ('Anderson .Paak');
 
insert into coda_album(album_title,artist_id,release_year)
values ('Gone Now',7,'2017');
insert into coda_album(album_title,artist_id,release_year)
values ('Born To Die',9,2012);
insert into coda_album(album_title,artist_id,release_year)
values ('Wasteland, Baby!',10,2019);
insert into coda_album(album_title,artist_id,release_year)
values ('Nectar',11,2020);
insert into coda_album(album_title,artist_id,release_year)
values ('Dear Annie',12,2018);
insert into coda_album(album_title,artist_id,release_year)
values ('Oxnard',13,2018);
 
insert into coda_song(song_title,genre,album_id,added_by)
values ('Don''t Take The Money','Indie Pop', 7, 4);
insert into coda_song(song_title,genre,album_id,added_by)
values ('Off To The Races','Pop', 13, 4);
insert into coda_song(song_title,genre,album_id,added_by)
values ('Wasteland, Baby!','Soul', 14, 4);
insert into coda_song(song_title,genre,album_id,added_by)
values ('Daylight','R&B', 15, 4);
insert into coda_song(song_title,genre,album_id,added_by)
values ('Charlie Brown','Hip-Hop', 16, 4);
insert into coda_song(song_title,genre,album_id,added_by)
values ('Tints','Hip-Hop', 17, 4);

insert into coda_playlist(playlist_name,created_by)
values ('Scary Girl Songs',4);

insert into coda_playlist_songs 
values(
(select playlist_id from coda_playlist 
 where playlist_name = 'Scary Girl Songs'),
(select song_id from coda_song
 where song_title = 'Off To The Races')
);

insert into coda_playlist(playlist_name,created_by)
values ('Upbeat Songs!',4);

insert into coda_playlist_songs 
values(
(select playlist_id from coda_playlist 
 where playlist_name = 'Upbeat Songs!'),
(select song_id from coda_song
 where song_title = 'Daylight')
);
insert into coda_playlist_songs 
values(
(select playlist_id from coda_playlist 
 where playlist_name = 'Upbeat Songs!'),
(select song_id from coda_song
 where song_title = 'Charlie Brown')
);

