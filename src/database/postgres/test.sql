CREATE TABLE users (
    userid SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    password VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE tasks (
    taskid SERIAL PRIMARY KEY,
    taskName VARCHAR(100) NOT NULL,
    taskDescipt VARCHAR(100) NOT NULL,
    startTime TIMESTAMP NOT NULL,
    endTime TIMESTAMP NOT NULL,
    color VARCHAR(100),
    priority INTEGER,
    status VARCHAR(100) NOT NULL
);


INSERT INTO users (name, email, age) VALUES
('Alice', 'alice@example.com', 25),
('Bob', 'bob@example.com', 30),
('Charlie', 'charlie@example.com', 22);


-- chay lenh nay de test db khi pull image ve
SELECT * FROM users;