use coda_db;

insert into coda_playlist(playlist_name, playlist_genre, created_by)
values ('lowkey chill vibes', 'Pop', 6);

insert into coda_playlist_songs 
values(
(select playlist_id from coda_playlist 
 where playlist_name = 'lowkey chill vibes'),
(select song_id from coda_song
 where song_title = 'Universe')
);
insert into coda_playlist_songs 
values(
(select playlist_id from coda_playlist 
 where playlist_name = 'lowkey chill vibes'),
(select song_id from coda_song
 where song_title = 'bandaids')
);
insert into coda_playlist_songs 
values(
(select playlist_id from coda_playlist 
 where playlist_name = 'lowkey chill vibes'),
(select song_id from coda_song
 where song_title = 'Malibu Nights')
);
insert into coda_playlist_songs 
values(
(select playlist_id from coda_playlist 
 where playlist_name = 'lowkey chill vibes'),
(select song_id from coda_song
 where song_title = 'High Tension')
);
insert into coda_playlist_songs 
values(
(select playlist_id from coda_playlist 
 where playlist_name = 'lowkey chill vibes'),
(select song_id from coda_song
 where song_title = 'Be My Mistake')
);