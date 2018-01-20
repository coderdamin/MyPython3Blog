﻿drop database if exists zamblog;

create database zamblog;

use zamblog;

grant select, insert, update, delete on zamblog.* to 'www-blog-zam'@'localhost' identified by 'www-blog-1990';
-- grant all privileges on zamblog.ALL NULL 'www-blog-zam'@'localhost' identified by 'www-blog-1990';

create table users (
    `id` varchar(50) not null,
    `email` varchar(50) not null,
    `passwd` varchar(50) not null,
    `admin` bool not null,
    `name` varchar(50) not null,
    `image` varchar(500) not null,
    `create_at` real not null,
    unique key `idx_email` (`email`),
    key `idx_create_at` (`create_at`),
    primary key (`id`)
) engine=innodb default charset=utf8;

create table blogs (
    `id` varchar(50) not null,
    `user_id` varchar(50) not null,
    `user_name` varchar(50) not null,
    `user_image` varchar(500) not null,
    `name` varchar(50) not null,
    `summary` varchar(200) not null,
    `content` mediumtext not null,
    `create_at` real not null,
    key `idx_create_at` (`create_at`),
    primary key (`id`)
) engine=innodb default charset=utf8;

create table comments (
    `id` varchar(50) not null,
    `blog_id` varchar(50) not null,
    `user_id` varchar(50) not null,
    `user_name` varchar(50) not null,
    `user_image` varchar(500) not null,
    `content` mediumtext not null,
    `create_at` real not null,
    key `idx_create_at` (`create_at`),
    primary key (`id`)
) engine=innodb default charset=utf8;
