# SQL queries

def get_update_start_and_end_date_query():
    return """
    UPDATE employee_work 
    SET start_date = CASE WHEN half_of_month = 1 
                            THEN date(date, 'start of month') 
                        ELSE date(date, 'start of month', '+15 days') 
                    END
        , end_date = CASE WHEN half_of_month = 1 
                            THEN date(date, 'start of month', '+14 days') 
                        ELSE date(date, 'start of month', '+1 month', '-1 day') 
                    END
    WHERE start_date IS NULL OR end_date IS NULL
    """

def get_payroll_report_query():
    return """
    SELECT 
        emp.employee_id
        , emp.start_date
        , emp.end_date
        , SUM(emp.hours_worked * hr.hourly_rate) AS total_amount_paid
    FROM employee_work emp
        INNER JOIN hourly_rates hr 
            ON emp.job_group = hr.job_group
    GROUP BY emp.employee_id
        , emp.start_date
        ,emp.end_date
    ORDER BY emp.employee_id
        , emp.start_date  
    """