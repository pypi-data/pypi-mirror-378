def trim_replace_special_character(sql: str, strip_sufix: bool = False) -> str:
    sql = sql.replace("\\n", "\n")  # todo: may cause error if \\n is in `like '%\\n%'` format
    # process \\n in sql
    if strip_sufix:
        sql = sql.strip(";")
    return sql
