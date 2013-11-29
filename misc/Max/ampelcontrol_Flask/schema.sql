drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  title text not null,
  morsecode text not null,
  duration integer not null
);