CREATE DATABASE db_ai_helpdesk;

use db_ai_helpdesk;

CREATE TABLE azure_users (
    user_id CHAR(36) PRIMARY KEY,
    user_name VARCHAR(255) NOT NULL,  
    user_group VARCHAR(20) NOT NULL
);

CREATE TABLE tickets (
    ticket_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,       
    content TEXT NOT NULL,             
    summary_vector JSON,                      
    creation_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,  
    closed_date DATETIME DEFAULT NULL,  
    author_id CHAR(36) NOT NULL,         
    assignee_id CHAR(36) DEFAULT NULL,  
    FOREIGN KEY (author_id) REFERENCES azure_users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (assignee_id) REFERENCES azure_users(user_id) ON DELETE SET NULL
);

CREATE TABLE ticket_messages (
    message_id INT AUTO_INCREMENT PRIMARY KEY,  
    ticket_id INT NOT NULL,                    
    author_id CHAR(36) NOT NULL,               
    message TEXT NOT NULL,                     
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,  
    FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES azure_users(user_id) ON DELETE CASCADE
);