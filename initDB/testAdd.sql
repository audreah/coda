use coda_db;

insert into coda_artist(artist_name) values ('Whee In');

insert into coda_album(album_title,artist_id)
values ('soar', (select artist_id from coda_artist where artist_name = 'Whee In'));

insert into coda_song(song_title,genre,album_id,added_by)
values ('Good Bye','Pop', 
(select album_id from coda_album where album_title = 'soar' 
and artist_id = (select artist_id from coda_artist where artist_name = 'Whee In')), 6);

