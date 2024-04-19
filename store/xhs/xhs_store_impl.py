# -*- coding: utf-8 -*-
# @Author  : relakkes@gmail.com
# @Time    : 2024/1/14 16:58
# @Desc    : 小红书存储实现类
import asyncio
import csv
import json
import os
import pathlib
from typing import Dict

import aiofiles

from base.base_crawler import AbstractStore
from tools import utils
from var import crawler_type_var


class XhsCsvStoreImplement(AbstractStore):
    csv_store_path: str = "data/xhs"

    def make_save_file_name(self, store_type: str) -> str:
        """
        make save file name by store type
        Args:
            store_type: contents or comments

        Returns: eg: data/xhs/search_comments_20240114.csv ...

        """
        return f"{self.csv_store_path}/{crawler_type_var.get()}_{store_type}_{utils.get_current_time_dot()}.csv"

    async def save_data_to_csv(self, save_item: Dict, store_type: str):
        """
        Below is a simple way to save it in CSV format.
        Args:
            save_item:  save content dict info
            store_type: Save type contains content and comments（contents | comments）

        Returns: no returns

        """
        pathlib.Path(self.csv_store_path).mkdir(parents=True, exist_ok=True)
        save_file_name = self.make_save_file_name(store_type=store_type)
        async with aiofiles.open(save_file_name, mode='a+', encoding="utf-8-sig", newline="") as f:
            f.fileno()
            writer = csv.writer(f)
            if await f.tell() == 0:
                await writer.writerow(save_item.keys())
            await writer.writerow(save_item.values())

    async def store_content(self, content_item: Dict):
        """
        Xiaohongshu content CSV storage implementation
        Args:
            content_item: note item dict

        Returns:

        """
        await self.save_data_to_csv(save_item=content_item, store_type="contents")

    async def store_comment(self, comment_item: Dict):
        """
        Xiaohongshu comment CSV storage implementation
        Args:
            comment_item: comment item dict

        Returns:

        """
        await self.save_data_to_csv(save_item=comment_item, store_type="comments")

    async def store_creator(self, creator: Dict):
        """
        Xiaohongshu content CSV storage implementation
        Args:
            creator: creator dict

        Returns:

        """
        await self.save_data_to_csv(save_item=creator, store_type="creator")


class XhsDbStoreImplement(AbstractStore):
    async def store_content(self, content_item: Dict):
        """
        Xiaohongshu content DB storage implementation
        Args:
            content_item: content item dict

        Returns:

        """
        from .xhs_store_sql import (add_new_content,
                                    query_content_by_content_id,
                                    update_content_by_content_id)
        note_id = content_item.get("note_id")
        note_detail: Dict = await query_content_by_content_id(content_id=note_id)
        if not note_detail:
            content_item["add_ts"] = utils.get_current_timestamp()
            await add_new_content(content_item)
        else:
            await update_content_by_content_id(note_id, content_item=content_item)

    async def store_comment(self, comment_item: Dict):
        """
        Xiaohongshu content DB storage implementation
        Args:
            comment_item: comment item dict

        Returns:

        """
        from .xhs_store_sql import (add_new_comment,
                                    query_comment_by_comment_id,
                                    update_comment_by_comment_id)
        comment_id = comment_item.get("comment_id")
        comment_detail: Dict = await query_comment_by_comment_id(comment_id=comment_id)
        if not comment_detail:
            comment_item["add_ts"] = utils.get_current_timestamp()
            await add_new_comment(comment_item)
        else:
            await update_comment_by_comment_id(comment_id, comment_item=comment_item)

    async def store_creator(self, creator: Dict):
        """
        Xiaohongshu content DB storage implementation
        Args:
            creator: creator dict

        Returns:

        """
        from .xhs_store_sql import (add_new_creator, query_creator_by_user_id,
                                    update_creator_by_user_id)
        user_id = creator.get("user_id")
        user_detail: Dict = await query_creator_by_user_id(user_id)
        if not user_detail:
            creator["add_ts"] = utils.get_current_timestamp()
            await add_new_creator(creator)
        else:
            await update_creator_by_user_id(user_id, creator)


class XhsJsonStoreImplement(AbstractStore):
    json_store_path: str = "data/xhs"
    lock = asyncio.Lock()

    def make_save_file_name(self, store_type: str) -> str:
        """
        make save file name by store type
        Args:
            store_type: Save type contains content and comments（contents | comments）

        Returns:

        """
        return f"{self.json_store_path}/{crawler_type_var.get()}_{store_type}_{utils.get_current_time_dot()}.json"

    async def save_data_to_json(self, save_item: Dict, store_type: str):
        """
        Below is a simple way to save it in json format.
        Args:
            save_item: save content dict info
            store_type: Save type contains content and comments（contents | comments）

        Returns:

        """
        pathlib.Path(self.json_store_path).mkdir(parents=True, exist_ok=True)
        save_file_name = self.make_save_file_name(store_type=store_type)
        save_data = []

        async with self.lock:
            if os.path.exists(save_file_name):
                async with aiofiles.open(save_file_name, 'r', encoding='utf-8') as file:
                    save_data = json.loads(await file.read())

            save_data.append(save_item)
            async with aiofiles.open(save_file_name, 'w', encoding='utf-8') as file:
                await file.write(json.dumps(save_data, ensure_ascii=False))

    async def store_content(self, content_item: Dict):
        """
        content JSON storage implementation
        Args:
            content_item:

        Returns:

        """
        await self.save_data_to_json(content_item, "contents")

    async def store_comment(self, comment_item: Dict):
        """
        comment JSON storage implementatio
        Args:
            comment_item:

        Returns:

        """
        await self.save_data_to_json(comment_item, "comments")

    async def store_creator(self, creator: Dict):
        """
        Xiaohongshu content JSON storage implementation
        Args:
            creator: creator dict

        Returns:

        """
        await self.save_data_to_json(creator, "creator")