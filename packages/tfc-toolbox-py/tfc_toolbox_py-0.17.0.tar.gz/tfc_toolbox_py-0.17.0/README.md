# tfc_toolbox_py
This is a tool box. You can use some tools to accelerate development efficiency.

Various tools made with Python, which can be directly called in modules.

## Install
You can install this package by pip:
```shell
pip install tfc_toolbox_py
```

## How to use it
```python
import tfc_toolbox_py as tfc
print(tfc.math.add(1, 2))
```

## Tools
### account
- [x] input password
- [x] change password
### math
- [x] add
- [x] subtract
- [x] get_fibonacci
- [x] get_fibonacci_sequence
### console
- [x] menu
### spider
- [ ] get_xiaohongshu_article
- [ ] get_xiaohongshu_comment
### cv
- [x] ImageStitcher
### verilog
- [x] generate_verilog_instance
### converter
- [x] binary_to_text
### cqupt
- [x] get_cqupt_schedule_text
- [x] get_cqupt_news
### webdav
- [x] webdav_client
### pip_manager
- [x] upgrade_check
- [x] upgrade_package
### office_operation
- [x] get_xlsx_column_data
### file_operation
- [x] read_file_to_list
- [x] save_list_to_file
- [x] get_file_name_from_folder
- [x] get_file_full_name_from_folder
- [x] get_file_and_folder_full_name_from_folder
### sqlite_manager
- [x] create_table
- [x] add_data
- [x] modify_data
- [x] delete_data_by_id
- [x] read_data_to_list
- [x] read_column_data_to_list
### mysql_manager
- [x] create_mysql_connection
- [x] execute_query