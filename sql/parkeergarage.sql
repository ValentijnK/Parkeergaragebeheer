create table cars
(
	id int auto_increment
		primary key,
	license_plate varchar(128) not null,
	garage_entry_time timestamp default CURRENT_TIMESTAMP not null,
	garage_leave_time timestamp null,
	email varchar(255) null
)
;

