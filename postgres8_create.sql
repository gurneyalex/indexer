/* 
Copyright Logilab 2002-2003, all rights reserved.

Creates the postgres Indexer database.
*/

drop index appears_uid;

drop table appears;

create table appears(
  uid     integer,
  words   tsvector
);

create index appears_uid on appears (uid);

