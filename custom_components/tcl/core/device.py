import json
import logging
from typing import List

from .attribute import TclAttribute, V1SpecAttributeParser

_LOGGER = logging.getLogger(__name__)


class TclDevice:
    _raw_data: dict
    _attributes: List[TclAttribute]
    _attribute_snapshot_data: dict

    def __init__(self, client, raw: dict):
        self._client = client
        self._raw_data = raw
        self._attributes = []
        self._attribute_snapshot_data = {}

    @property
    def id(self):
        return self._raw_data['deviceId']

    @property
    def name(self):
        return self._raw_data['nickName'] if 'nickName' in self._raw_data else self.id

    @property
    def type(self):
        return self._raw_data['category'] if 'category' in self._raw_data else None

    @property
    def product_key(self):
        return self._raw_data['productKey'] if 'productKey' in self._raw_data else None

    @property
    def is_online(self):
        return self._raw_data['isOnline'] if 'isOnline' in self._raw_data else None

    @property
    def is_control(self):
        return self._raw_data['weChatControl']

    @property
    def attributes(self) -> List[TclAttribute]:
        return self._attributes

    @property
    def attribute_snapshot_data(self) -> dict:
        return self._attribute_snapshot_data

    @property
    def getClient(self):
        return self._client

    def update_attribute_snapshot_data(self, new_data: dict):
        # 可以在这里添加数据验证逻辑
        self._attribute_snapshot_data = new_data

    async def async_init(self):
        # 解析Attribute
        # noinspection PyBroadException
        try:
            parser = V1SpecAttributeParser()
            attributes = await self._client.get_digital_model_from_cache(self)

            for item in attributes:
                try:
                    # item.value=snapshot_data[item['identifier']]
                    attr = parser.parse_attribute(item)
                    if attr:
                        self._attributes.append(attr)
                except:
                    _LOGGER.exception("Tcl device %s attribute %s parsing error occurred", self.id, item['name'])
            snapshot_data = await self._client.get_device_snapshot_data(self.id)
            _LOGGER.debug(
                'device %s snapshot data fetch successful. data: %s',
                self.id,
                json.dumps(snapshot_data)
            )
            self._attribute_snapshot_data = snapshot_data
        except Exception:
            _LOGGER.exception('Tcl device %s init failed', self.id)

    def __str__(self) -> str:
        return json.dumps({
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'product_key': self.product_key,
            'is_online': self.is_online,
            'is_control': self.is_control
        })
