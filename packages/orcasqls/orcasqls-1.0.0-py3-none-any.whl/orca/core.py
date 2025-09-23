# orca/core.py
class _SQLStudy:
    # ================ EXERCISE 1: TABLE CREATION ================
    def create_department(self):
        print("""
CREATE TABLE DEPARTMENT(
    DEPARTMENT_ID VARCHAR(6) PRIMARY KEY CHECK(DEPARTMENT_ID LIKE 'D%'),
    DEPARTMENT_NAME VARCHAR(20),
    MANAGER_ID INT,
    LOCATION VARCHAR(20)
);
        """)

    def create_employee(self):
        print("""
CREATE TABLE EMPLOYEE1(
    EMPLOYEE_ID VARCHAR(6) PRIMARY KEY CHECK(EMPLOYEE_ID LIKE 'E%'),
    FIRSTNAME VARCHAR(20),
    LASTNAME VARCHAR(20),
    BIRTHDATE DATE,
    GENDER CHAR(1),
    DEPARTMENT_ID VARCHAR(6),
    SALARY NUMBER(10,2) DEFAULT 5000,
    FOREIGN KEY(DEPARTMENT_ID) REFERENCES DEPARTMENT(DEPARTMENT_ID)
);
        """)

    def create_project(self):
        print("""
CREATE TABLE PROJECT(
    PROJECT_ID VARCHAR(9) PRIMARY KEY CHECK (PROJECT_ID LIKE 'P%'),
    PROJECT_NAME VARCHAR2(50),
    PROJECT_LOCATION VARCHAR(100),
    DEPARTMENT_ID VARCHAR(6),
    PROJECT_BUDGET NUMBER(12,2),
    FOREIGN KEY(DEPARTMENT_ID) REFERENCES DEPARTMENT(DEPARTMENT_ID)
);
        """)

    # ================ EXERCISE 1: INSERTIONS ================
    def insert_department(self):
        print("""
INSERT INTO DEPARTMENT VALUES('D101', 'HUMAN RESOUCES', 1, 'NEW YORK');
INSERT INTO DEPARTMENT VALUES('D102', 'FINANCE', 2, 'CHICAGO');
INSERT INTO DEPARTMENT VALUES('D103', 'MARKETING', 3, 'LOS ANGELES');
INSERT INTO DEPARTMENT VALUES('D104', 'ENGINEERING', 4, 'SAN FRANCISCO');
INSERT INTO DEPARTMENT VALUES('D105', 'SALES', 5, 'HOUSTON');
        """)

    def insert_employee(self):
        print("""
INSERT INTO EMPLOYEE1 VALUES('E1','JOHN','DOE','15-JAN-90','M','D101',50000);
INSERT INTO EMPLOYEE1 VALUES('E2','JANE','SMITH','20-MAR-95','F','D102',55000);
INSERT INTO EMPLOYEE1 VALUES('E3','MIKE','JOHNSON','10-NOV-88','M','D101',60000);
INSERT INTO EMPLOYEE1 VALUES('E4','EMILY','DAVIS','05-JUL-92','F','D103',52000);
INSERT INTO EMPLOYEE1 VALUES('E5','DAVID','WILSON','25-APR-97','M','D102',58000);
        """)

    def insert_project(self):
        print("""
INSERT INTO PROJECT VALUES('P1','PROJECT A', 'NEWYORK','D101',100000);
INSERT INTO PROJECT VALUES('P2','PROJECT B', 'CHICAGO','D102',75000);
INSERT INTO PROJECT VALUES('P3','PROJECT C', 'LOS ANGELES','D103',125000);
INSERT INTO PROJECT VALUES('P4','PROJECT D', 'SAN FRANCISCO','D104',90000);
INSERT INTO PROJECT VALUES('P5','PROJECT E', 'HOUSTON','D105',80000);
        """)

    # ================ EXERCISE 2: ALTER TABLES ================
    def alter_rename_department_to_dept1(self):
        print("RENAME DEPARTMENT TO DEPT1;")

    def alter_add_address_to_employee(self):
        print("ALTER TABLE EMPLOYEE1 ADD(ADDRESS VARCHAR(20));")

    def alter_rename_dept_name_column(self):
        print("ALTER TABLE DEPT1 RENAME COLUMN DEPARTMENT_NAME TO DEPT_NAME;")

    def alter_drop_manager_id(self):
        print("ALTER TABLE DEPT1 DROP COLUMN MANAGER_ID;")

    def alter_add_manager_id_fk(self):
        print("ALTER TABLE DEPT1 ADD MANAGER_ID REFERENCES EMPLOYEE1(EMPLOYEE_ID);")

    # ================ EXERCISE 3 & 4: QUERIES ================
    def query_employees_in_d102(self):
        print("SELECT * FROM EMPLOYEE1 WHERE DEPARTMENT_ID='D102';")

    def query_projects_budget_50k_to_100k(self):
        print("SELECT * FROM PROJECT WHERE PROJECT_BUDGET>50000 AND PROJECT_BUDGET<=100000;")

    def query_departments_in_new_york(self):
        print("SELECT * FROM DEPT1 WHERE LOCATION='NEW YORK';")

    def query_count_distinct_firstnames(self):
        print("SELECT COUNT(DISTINCT FIRSTNAME) FROM EMPLOYEE1;")

    def query_j_names_salary_ge_50k(self):
        print("SELECT * FROM EMPLOYEE1 WHERE FIRSTNAME LIKE 'J%' AND SALARY>=50000;")

    def query_names_between_a_and_l(self):
        print("SELECT * FROM EMPLOYEE1 WHERE FIRSTNAME>'A' AND FIRSTNAME<'L';")

    def query_names_start_n_fourth_i(self):
        print("SELECT * FROM EMPLOYEE1 WHERE FIRSTNAME LIKE 'N__I%';")

    def query_dept_d101_d102_d103(self):
        print("SELECT * FROM DEPT1 WHERE DEPARTMENT_ID IN('D101','D102','D103');")

    def query_salary_above_average(self):
        print("SELECT * FROM EMPLOYEE1 WHERE SALARY>(SELECT AVG(SALARY) FROM EMPLOYEE1);")

    def query_projects_hr_not_finance(self):
        print("""
SELECT * FROM PROJECT WHERE DEPARTMENT_ID=(SELECT DEPARTMENT_ID FROM DEPT1 WHERE DEPT_NAME='HUMAN RESOUCES')
MINUS
SELECT * FROM PROJECT WHERE DEPARTMENT_ID=(SELECT DEPARTMENT_ID FROM DEPT1 WHERE DEPT_NAME='FINANCE');
        """)

    def query_oldest_employee(self):
        print("SELECT * FROM EMPLOYEE1 WHERE BIRTHDATE=(SELECT MIN(BIRTHDATE) FROM EMPLOYEE1);")

    # ================ EXERCISE 5: GROUP BY / ORDER BY ================
    def query_order_employees_by_salary(self):
        print("SELECT * FROM EMPLOYEE1 ORDER BY SALARY;")

    def query_dept_avg_budget_gt_5000(self):
        print("""
SELECT D.DEPT_NAME
FROM DEPT1 D
JOIN PROJECT P ON D.DEPARTMENT_ID = P.DEPARTMENT_ID
GROUP BY D.DEPT_NAME
HAVING AVG(P.PROJECT_BUDGET) > 5000
ORDER BY D.DEPT_NAME;
        """)

    def query_projects_budget_gt_10000(self):
        print("SELECT * FROM PROJECT WHERE PROJECT_BUDGET > 10000 ORDER BY PROJECT_BUDGET;")

    # ================ EXERCISE 6: JOINS ================
    def join_employees_in_marketing(self):
        print("""
SELECT EMPLOYEE1.FIRSTNAME, DEPT1.DEPT_NAME
FROM EMPLOYEE1 JOIN DEPT1 ON EMPLOYEE1.DEPARTMENT_ID = DEPT1.DEPARTMENT_ID
WHERE DEPT1.DEPT_NAME = 'MARKETING';
        """)

    def left_join_dept_with_employees(self):
        print("""
SELECT DEPT1.DEPT_NAME, FIRSTNAME || ' ' || LASTNAME AS NAME
FROM DEPT1 LEFT JOIN EMPLOYEE1 ON DEPT1.DEPARTMENT_ID = EMPLOYEE1.DEPARTMENT_ID;
        """)

    def right_join_employees_with_projects(self):
        print("""
SELECT PROJECT_NAME, FIRSTNAME || ' ' || LASTNAME AS NAME
FROM PROJECT RIGHT JOIN EMPLOYEE1 ON EMPLOYEE1.DEPARTMENT_ID = PROJECT.DEPARTMENT_ID;
        """)

    # ================ EXERCISE 7: PL/SQL BLOCKS ================
    def plsql_swap_two_numbers(self):
        print("""
DECLARE
    num1 NUMBER;
    num2 NUMBER;
    temp NUMBER;
BEGIN
    num1 := &Enter_first_number;
    num2 := &Enter_second_number;
    DBMS_OUTPUT.PUT_LINE('Before Swapping:');
    DBMS_OUTPUT.PUT_LINE('num1 = ' || num1 || ', num2 = ' || num2);
    temp := num1;
    num1 := num2;
    num2 := temp;
    DBMS_OUTPUT.PUT_LINE('After Swapping:');
    DBMS_OUTPUT.PUT_LINE('num1 = ' || num1 || ', num2 = ' || num2);
END;
/
        """)

    def plsql_largest_of_three(self):
        print("""
DECLARE
    a NUMBER := 25;
    b NUMBER := 40;
    c NUMBER := 30;
    largest NUMBER;
BEGIN
    IF a > b THEN
        IF a > c THEN
            largest := a;
        ELSE
            largest := c;
        END IF;
    ELSE
        IF b > c THEN
            largest := b;
        ELSE
            largest := c;
        END IF;
    END IF;
    DBMS_OUTPUT.PUT_LINE('The largest number is: ' || largest);
END;
/
        """)

    def plsql_sum_of_digits(self):
        print("""
DECLARE
    num NUMBER := 12345;
    sum_of_digits NUMBER := 0;
    digit NUMBER;
BEGIN
    WHILE num > 0 LOOP
        digit := MOD(num, 10);
        sum_of_digits := sum_of_digits + digit;
        num := FLOOR(num / 10);
    END LOOP;
    DBMS_OUTPUT.PUT_LINE('Sum of digits: ' || sum_of_digits);
END;
/
        """)

    def plsql_prime_check(self):
        print("""
DECLARE
    num NUMBER := 29;
    i NUMBER := 2;
    is_prime BOOLEAN := TRUE;
BEGIN
    IF num <= 1 THEN
        is_prime := FALSE;
    ELSE
        WHILE i <= FLOOR(num / 2) LOOP
            IF MOD(num, i) = 0 THEN
                is_prime := FALSE;
                EXIT;
            END IF;
            i := i + 1;
        END LOOP;
    END IF;
    IF is_prime THEN
        DBMS_OUTPUT.PUT_LINE(num || ' is a prime number.');
    ELSE
        DBMS_OUTPUT.PUT_LINE(num || ' is not a prime number.');
    END IF;
END;
/
        """)

    def plsql_area_of_circle(self):
        print("""
DECLARE
    radius NUMBER := &ENTER_RADIUS;
    area NUMBER;
BEGIN
    area := 3.14159 * radius * radius;
    DBMS_OUTPUT.PUT_LINE('The area of the circle with radius ' || radius || ' is: ' || area);
END;
/
        """)

    # ================ EXERCISE 8: TRIGGERS ================
    def trigger_show_stipend_change(self):
        print("""
CREATE TABLE stu (
    student_id NUMBER PRIMARY KEY,
    name VARCHAR2(100),
    stipend NUMBER
);

INSERT INTO stu (student_id, name, stipend) VALUES (1, 'Alice', 1000);

CREATE OR REPLACE TRIGGER trg_stipend_update_stu
    AFTER UPDATE ON stu
    FOR EACH ROW
BEGIN
    IF NVL(:OLD.stipend, -1) != NVL(:NEW.stipend, -1) THEN
        DBMS_OUTPUT.PUT_LINE('Stipend updated:');
        DBMS_OUTPUT.PUT_LINE('Old Stipend: ' || :OLD.stipend);
        DBMS_OUTPUT.PUT_LINE('New Stipend: ' || :NEW.stipend);
    END IF;
END;
/
        """)

    def trigger_backup_on_update_delete(self):
        print("""
CREATE TABLE backup_stud (
    student_id NUMBER,
    name VARCHAR2(100),
    stipend NUMBER,
    action_type VARCHAR2(10),
    action_date DATE
);

CREATE OR REPLACE TRIGGER trg_backup_stu
    BEFORE UPDATE OR DELETE ON stu
    FOR EACH ROW
DECLARE
    v_action_type VARCHAR2(10);
BEGIN
    v_action_type := CASE WHEN UPDATING THEN 'UPDATE' ELSE 'DELETE' END;
    INSERT INTO backup_stud (student_id, name, stipend, action_type, action_date)
    VALUES (:OLD.student_id, :OLD.name, :OLD.stipend, v_action_type, SYSDATE);
END;
/
        """)

    # ================ EXERCISE 9: PROCEDURES & FUNCTIONS ================
    def procedure_smallest_of_three(self):
        print("""
CREATE OR REPLACE PROCEDURE find_smallest(
    a IN NUMBER,
    b IN NUMBER,
    c IN NUMBER,
    smallest OUT NUMBER
) IS
BEGIN
    IF a <= b AND a <= c THEN
        smallest := a;
    ELSIF b <= a AND b <= c THEN
        smallest := b;
    ELSE
        smallest := c;
    END IF;
END;
/
        """)

    def procedure_square_of_number(self):
        print("""
CREATE OR REPLACE PROCEDURE find_square (
    num IN NUMBER,
    square OUT NUMBER
) IS
BEGIN
    square := num * num;
END;
/
        """)

    def function_factorial(self):
        print("""
CREATE OR REPLACE FUNCTION factorial(n IN NUMBER) RETURN NUMBER IS
    result NUMBER := 1;
BEGIN
    IF n < 0 THEN
        RETURN NULL;
    END IF;
    FOR i IN 1..n LOOP
        result := result * i;
    END LOOP;
    RETURN result;
END;
/
        """)

    def function_palindrome(self):
        print("""
CREATE OR REPLACE FUNCTION palindrom(num IN NUMBER) RETURN VARCHAR2 IS
    original NUMBER := num;
    reversed NUMBER := 0;
    remainder NUMBER;
    temp NUMBER := num;
BEGIN
    WHILE temp > 0 LOOP
        remainder := MOD(temp, 10);
        reversed := (reversed * 10) + remainder;
        temp := TRUNC(temp / 10);
    END LOOP;
    IF original = reversed THEN
        RETURN 'Palindrome';
    ELSE
        RETURN 'Not Palindrome';
    END IF;
END;
/
        """)

    # ================ EXERCISE 10: PACKAGES ================
    def package_geometry_spec(self):
        print("""
CREATE OR REPLACE PACKAGE geometry_pkg AS
    FUNCTION area_circle(radius NUMBER) RETURN NUMBER;
    FUNCTION area_triangle(base NUMBER, height NUMBER) RETURN NUMBER;
    FUNCTION area_rectangle(length NUMBER, width NUMBER) RETURN NUMBER;
    FUNCTION volume_cylinder(radius NUMBER, height NUMBER) RETURN NUMBER;
END geometry_pkg;
/
        """)

    def package_geometry_body(self):
        print("""
CREATE OR REPLACE PACKAGE BODY geometry_pkg AS
    FUNCTION area_circle(radius NUMBER) RETURN NUMBER IS BEGIN RETURN 3.14159 * radius * radius; END;
    FUNCTION area_triangle(base NUMBER, height NUMBER) RETURN NUMBER IS BEGIN RETURN 0.5 * base * height; END;
    FUNCTION area_rectangle(length NUMBER, width NUMBER) RETURN NUMBER IS BEGIN RETURN length * width; END;
    FUNCTION volume_cylinder(radius NUMBER, height NUMBER) RETURN NUMBER IS BEGIN RETURN 3.14159 * radius * radius * height; END;
END geometry_pkg;
/
        """)

    def package_arithmetic_spec(self):
        print("""
CREATE OR REPLACE PACKAGE arithmetic_pkg AS
    FUNCTION add_numbers(a NUMBER, b NUMBER) RETURN NUMBER;
    FUNCTION subtract_numbers(a NUMBER, b NUMBER) RETURN NUMBER;
    FUNCTION multiply_numbers(a NUMBER, b NUMBER) RETURN NUMBER;
    FUNCTION divide_numbers(a NUMBER, b NUMBER) RETURN NUMBER;
END arithmetic_pkg;
/
        """)

    def package_arithmetic_body(self):
        print("""
CREATE OR REPLACE PACKAGE BODY arithmetic_pkg AS
    FUNCTION add_numbers(a NUMBER, b NUMBER) RETURN NUMBER IS BEGIN RETURN a + b; END;
    FUNCTION subtract_numbers(a NUMBER, b NUMBER) RETURN NUMBER IS BEGIN RETURN a - b; END;
    FUNCTION multiply_numbers(a NUMBER, b NUMBER) RETURN NUMBER IS BEGIN RETURN a * b; END;
    FUNCTION divide_numbers(a NUMBER, b NUMBER) RETURN NUMBER IS
    BEGIN
        IF b = 0 THEN RAISE_APPLICATION_ERROR(-20001, 'Division by zero is not allowed'); END IF;
        RETURN a / b;
    END;
END arithmetic_pkg;
/
        """)

    # ================ EXERCISE 11: CURSORS ================
    def cursor_create_student_table(self):
        print("""
CREATE TABLE STUDENT(
    ROLLNO NUMBER,
    NAME VARCHAR(10),
    TOTAL NUMBER,
    STIP NUMBER
);

INSERT INTO STUDENT VALUES(101,'OLIVIA',450,750);
INSERT INTO STUDENT VALUES(102,'AVA',290,288);
INSERT INTO STUDENT VALUES(103,'ISABELLA',550,432);
INSERT INTO STUDENT VALUES(104,'MIA',440,432);
INSERT INTO STUDENT VALUES(105,'ETHAN',350,288);
        """)

    def cursor_classify_students(self):
        print("""
DECLARE
    CURSOR student_cur IS SELECT * FROM student;
    v_percentage NUMBER;
    v_class VARCHAR2(20);
BEGIN
    FOR stu IN student_cur LOOP
        v_percentage := (stu.total / 600) * 100;
        IF v_percentage >= 80 THEN v_class := 'Distinction';
        ELSIF v_percentage >= 60 THEN v_class := 'First class';
        ELSIF v_percentage >= 50 THEN v_class := 'Second class';
        ELSE v_class := 'Fail'; END IF;
        DBMS_OUTPUT.PUT_LINE('Register Number: ' || stu.rollno || ' Student Name: ' || stu.name);
        DBMS_OUTPUT.PUT_LINE('Percentage: ' || ROUND(v_percentage) || '% Class: ' || v_class);
        DBMS_OUTPUT.PUT_LINE('-----------------------------');
    END LOOP;
END;
/
        """)

    def cursor_update_stipend_above_75(self):
        print("""
DECLARE
    CURSOR stipend_cur IS SELECT * FROM student;
    v_percentage NUMBER;
    v_new_stip NUMBER;
BEGIN
    FOR stu IN stipend_cur LOOP
        v_percentage := (stu.total / 600) * 100;
        IF v_percentage > 75 THEN
            v_new_stip := stu.stip * 1.2;
            UPDATE student SET stip = v_new_stip WHERE rollno = stu.rollno;
            DBMS_OUTPUT.PUT_LINE('REGISTER NUMBER : ' || stu.rollno || ' STUDENT NAME : ' || stu.name || ' STIPEND : ' || stu.stip || ' RS');
            DBMS_OUTPUT.PUT_LINE('NEW STIPEND: ' || v_new_stip || ' RS');
            DBMS_OUTPUT.PUT_LINE('-----------------------------');
        END IF;
    END LOOP;
    COMMIT;
END;
/
        """)

    def cursor_update_specific_student(self):
        print("""
DECLARE
    v_roll_no NUMBER := 101;
    CURSOR c IS SELECT * FROM student WHERE rollno = v_roll_no;
    v_new_stip NUMBER;
BEGIN
    FOR stu IN c LOOP
        v_new_stip := stu.stip * 1.2;
        UPDATE student SET stip = v_new_stip WHERE rollno = stu.rollno;
        DBMS_OUTPUT.PUT_LINE('REGISTER NUMBER: ' || stu.rollno || ' STUDENT NAME: ' || stu.name || ' NEW STIPEND: ' || v_new_stip || ' RS');
    END LOOP;
    COMMIT;
END;
/
        """)


# Export instance
study = _SQLStudy()