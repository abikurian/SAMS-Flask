CREATE DATABASE IF NOT EXISTS sams_db;
USE sams_db;

CREATE TABLE students (
  id INT AUTO_INCREMENT PRIMARY KEY,
  roll_no VARCHAR(20) UNIQUE NOT NULL,
  name VARCHAR(100) NOT NULL,
  department VARCHAR(50),
  year INT,
  email VARCHAR(100),
  phone VARCHAR(20)
);

CREATE TABLE subjects (
  id INT AUTO_INCREMENT PRIMARY KEY,
  code VARCHAR(20) UNIQUE NOT NULL,
  name VARCHAR(100) NOT NULL,
  department VARCHAR(50)
);

CREATE TABLE attendance (
  id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  subject_id INT NOT NULL,
  date DATE NOT NULL,
  status ENUM('P','A') NOT NULL,
  FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
  FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
  UNIQUE KEY (student_id, subject_id, date)
);

CREATE TABLE marks (
  id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT NOT NULL,
  subject_id INT NOT NULL,
  exam_type VARCHAR(50),
  marks_obtained DECIMAL(7,2),
  max_marks DECIMAL(7,2),
  FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
  FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);

-- sample data
INSERT INTO students (roll_no, name, department, year, email, phone)
VALUES
('SNG21CS001', 'Alice Varghese', 'CSE', 3, 'alice@example.com', '9876543210'),
('SNG21CS002', 'Bob Thomas', 'CSE', 3, 'bob@example.com', '9876501234'),
('SNG21CS003', 'Charlie Joy', 'IT', 2, 'charlie@example.com', '9898989898');

INSERT INTO subjects (code, name, department)
VALUES
('CS301', 'Database Systems', 'CSE'),
('CS302', 'Operating Systems', 'CSE'),
('IT201', 'Data Structures', 'IT');

-- sample attendance (two dates)
INSERT INTO attendance (student_id, subject_id, date, status) VALUES
(1,1,'2025-10-01','P'),
(2,1,'2025-10-01','A'),
(3,1,'2025-10-01','P'),
(1,1,'2025-10-02','P'),
(2,1,'2025-10-02','P');

-- sample marks
INSERT INTO marks (student_id, subject_id, exam_type, marks_obtained, max_marks) VALUES
(1,1,'Internal-1', 18, 20),
(2,1,'Internal-1', 15, 20),
(3,1,'Internal-1', 17, 20),
(1,2,'Internal-1', 16, 20);
