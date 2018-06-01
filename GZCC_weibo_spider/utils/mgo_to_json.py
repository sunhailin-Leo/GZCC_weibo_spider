# -*- coding: UTF-8 -*-
"""
Created on 2018年5月23日
@author: Leo
"""
import json
# 第三方库
import pymongo


class MongoToJson:
    def __init__(self,
                 db_name,
                 collection_name,
                 host="127.0.0.1",
                 port=27017,
                 username="",
                 password=""):
        """
        连接MongoDB
        :param db_name: 数据库名称
        :param collection_name: 集合名
        :param host: IP地址
        :param port: 端口号
        :param username: 用户名 (不必须)
        :param password: 密码 (不必须)
        """
        if username == "" and password == "":
            conn = pymongo.MongoClient(host=host,
                                       port=port)
        else:
            conn = pymongo.MongoClient(host=host,
                                       port=port,
                                       username=username,
                                       password=password)
        # 集合对象
        self._col = conn[db_name][collection_name]

    def load_data(self, query=None, filter_query=None, sort=None, sort_key_or_list=None):
        """
        加载数据
        :param query: 查询语句
        :param filter_query: 过滤语句
        :param sort: 结果排序方式(默认升序)
        :param sort_key_or_list: 排序的单个字段或多个字段(单个用字符串, 多个用list)
        :return:返回数据
        """
        # 判断查询语句是否为空
        if query is None:
            query = {}
        # 判断过滤语句是否为空
        if filter_query is None:
            filter_query = None
        if sort is not None:
            if sort_key_or_list is not None:
                # 判断数据类型
                if isinstance(sort_key_or_list, (str, list)):
                    if sort == pymongo.ASCENDING:
                        result = self._col.find(query, filter_query).sort(sort_key_or_list, sort)
                        return result.count(), [item for item in result]
                    elif sort == pymongo.DESCENDING:
                        result = self._col.find(query, filter_query).sort(sort_key_or_list, sort)
                        return result.count(), [item for item in result]
                    else:
                        raise ValueError("Error sort type!")
                else:
                    raise TypeError("Error sort argument! The argument must be str or list!")
            else:
                raise ValueError("sort argument is None!")
        else:
            result = self._col.find(query, filter_query)
            return result.count(), [item for item in result]

    @staticmethod
    def to_json(method, file_name=None):
        """
        数据转json
        :param method: 传入一个方法
        :param file_name: 文件名
        :return: json串或者是None
        """
        data_count, data = method
        json_data = json.dumps({"data": data, "count": data_count},
                               ensure_ascii=False,
                               indent=4)
        if data_count > 0:
            if file_name is None:
                return json_data
            else:
                with open("../../{}.json".format(file_name), 'w', encoding="utf-8") as f:
                    f.write(json_data)
                    f.close()
                return None
        else:
            return None


if __name__ == '__main__':
    t = MongoToJson(db_name="gzcc_weibo",
                    collection_name="weibo_user")
    r = t.to_json(method=t.load_data(filter_query={"_id": 0}), file_name="test")
    print(r)
