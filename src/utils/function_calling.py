import os
import json
from datetime import datetime
### TEST
def get_user_name():
    return "user's name: dinh van dang"
def get_weather(latitude, longitude):
    return "the current temperature: 39 celcius"

### SAVE CONSTRAINT
def saving_constraint(content):
    """
    Lưu constraint thì lưu vào mongodb 
    """
    pass
# LOAD CONSTRAINT
def reading_constraint(query):
    """
    query từ mongodb query với timestamp from start to end 
    """
    pass
    
# DOMAIN 
def domain_asking(query:str):
    """
    lấy dữ liệu trong chromadb (nếu có) + trigger gg search -> rerank lấy kết quả
    """
    pass

# DATABASE QUERY
def database_asking(query:str):
    """
    Query thông tin người dùng từ postgres 
    Query tổng quan dự đoán về người dùng từ mongoddb
    format lại message
    """
    pass

# DATABASE ADD TASK 
def database_addtask(query):
    """
    Thêm task vào lịch, schema cho trước, dùng api query db
    """
    pass
