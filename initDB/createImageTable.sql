drop table if exists picfile;
create table picfile (
    album_id int primary key,
    filename varchar(50),
    foreign key (album_id) references coda_album(album_id) 
        on delete cascade on update cascade
);
describe picfile;
