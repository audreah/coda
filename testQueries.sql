-- gets all playlists of a user given their id
select playlist_name, playlist_genre, user_name
from coda_playlist 
    inner join coda_user on (coda_user.user_id = coda_playlist.created_by)
where created_by = 4;

-- gets playlist info given an id
select playlist_name, playlist_genre, user_name
from coda_playlist 
    inner join coda_user on (coda_user.user_id = coda_playlist.created_by)
where playlist_id = 4;

-- gets songs in a playlist
select song_title 
from coda_song 
    inner join coda_playlist_songs using (song_id)
where playlist_id = 5;