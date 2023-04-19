import hashlib
import sys
import time
import traceback
sys.path.append("/app/scripts/")
from app.base import Base
from utils.db_helper import get_db


class DeliverPlace(Base):
    def __init__(self):
        super().__init__()
        self._url = "https://cn-ali-gw.fordeal.com/merchant/dwp.galio.getDeliverPlaceInfo/1"
        query_sql = (
            "select a.`id`, i.`shopId`, i.`shopName`, a.`username`, a.`password`"
            " from `accounts` as a left join `shops` as i on a.`shop_id`=i.`shopId`"
            f" where a.`username`='{self._username}' limit 1"
        )
        self._account = get_db().query_row(query_sql).to_dict()

    def request_handle(self):
        """
        请求预处理
        :return:
        """
        try:
            # 构造请求参数
            timestamp = int(round(time.time() * 1000))
            request_params = {
                "data": "{}",
                "gw_ver": 1,
                "ct": timestamp,
                "plat": "h5",
                "appname": "fordeal",
                "sign: ": hashlib.md5(str(timestamp).encode()).hexdigest(),
            }
            # 请求接口
            resp = self._requests_get(self._account, request_params)
            # 数据存储
            self._parse_and_save(resp, self._account['shopId'])
        except Exception as e:
            print(e)
            traceback.print_exc()

    def _parse_and_save(self, resp, shop_id):
        """
        数据入库
        :param resp:
        :param shop_id:
        :return:
        """
        resp_json = resp.json()
        if resp.status_code == 200 and resp_json['code'] == 1001:
            data = resp_json['data']
            for val in data:
                val['shopId'] = shop_id
                exist_sql = (
                    f"select * from `deliver_places` where `shopId`=%(shopId)s and `deliverPlaceCode`=%(deliverPlaceCode)s limit 1"
                )
                exist = get_db().query_row(exist_sql, {"shopId": shop_id, "deliverPlaceCode": val['deliverPlaceCode']})
                if exist.empty:
                    get_db().insert("deliver_places", val)
                else:
                    get_db().update("deliver_places", val, f"id={exist['id']}")
        else:
            raise Exception(resp_json['msg'])


if __name__ == '__main__':
    DeliverPlace().request_handle()
