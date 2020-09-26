use coda_db;
 
insert into coda_user(user_name) values ('Fred');
insert into coda_user(user_name) values ('George');
 
insert into coda_friend(friend_one,friend_two) values (1,2);
insert into coda_friend(friend_two,friend_one) values (1,2);
 
insert into coda_artist(artist_name) values ('Taylor Swift');
 
insert into coda_album(album_title,artist_id,release_year)
values ('Folklore',1,'2020');
 
insert into coda_song(song_title,genre,album_id,added_by)
values ('Betty','Country', 1, 1);
insert into coda_song(song_title,genre,album_id,added_by) 
values ('Peace','Alternative', 1, 1);
 
 
insert into coda_playlist(playlist_name,playlist_genre,created_by)
values ('Favorites of George','Country',2);
 
insert into coda_playlist_songs values(1,2);
insert into coda_playlist_songs 
values(
(select playlist_id from coda_playlist 
 where playlist_name = 'Favorites of George'),
(select song_id from coda_song
 where song_title = 'Betty')
);
