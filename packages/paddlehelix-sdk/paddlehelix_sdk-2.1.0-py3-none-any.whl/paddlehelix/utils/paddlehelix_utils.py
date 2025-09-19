import os
import json

import numpy as np
import pandas as pd

from paddlehelix.api.config import MAX_TASK_COUNT
from paddlehelix.api.task import TaskUtil


def ask_yes_no(question, logger):
    while True:
        user_input = input(question + " (Y/N): ").strip().upper()
        if user_input in ['Y', 'N']:
            return user_input == 'Y'
        else:
            logger.warning("Invalid input, please input Y or N.")


def check_existing_submission(output_dir, logger, quiet=False):
    """
    检查是否存在旧的提交，并询问用户是否要重新开始
    
    Args:
        output_dir: 输出目录
        logger: 日志记录器
        
    Returns:
        tuple: (success, dataframe)
            - 成功时返回 (True, dataframe)
            - 失败时返回 (False, None)
    """
    table_path = os.path.join(output_dir, "table.csv")
    df = pd.read_csv(table_path)
    
    if len(df) > 0:
        logger.info(f"Found tasks:")
        for index, row in df.iterrows():
            logger.info(f"{row['data']}")
        logger.info(f"Old submission under folder: {output_dir} ...")
        if not quiet and not ask_yes_no(f"Do you want to restart the submission under folder: {output_dir} ?", logger):
            logger.info(f"Exit.")
            return False, None
        return True, df
    else:
        logger.error(f"Task records are invalid under folder: {output_dir}")
        logger.error(f"Exit! Please check the folder or start a new submission!")
        return False, None


def init_input(output_dir, status, input_data=None, **kwargs):
    if 'task_ids' in kwargs:
        task_ids = kwargs['task_ids']
        if len(task_ids) > MAX_TASK_COUNT:
            raise ValueError(f"The number of tasks is too large: {len(task_ids)}. The maximum number of tasks is: {MAX_TASK_COUNT}.")
        if len(task_ids) == 0:
            raise ValueError(f"The number of tasks is 0.")
    else:
        task_ids = None

    df = pd.DataFrame(columns=['task_id', 'status', 'price', 'data', 'download_url'])
    if task_ids is not None:
        df['task_id'] = task_ids
        df['status'] = status
        df['price'] = np.nan
        df['data'] = ""
        df['download_url'] = ""
        df['storage_path'] = ""
        df.to_csv(os.path.join(output_dir, "table.csv"), index=False)
    else:
        task_list = TaskUtil.parse_task_data_list_from_all_kinds_input(input_data, **kwargs)
        df['data'] = [json.dumps(task) for task in task_list]
        df['task_id'] = -1
        df['download_url'] = ""
        df['status'] = status
        df['price'] = np.nan
        df['storage_path'] = ""
        df.to_csv(os.path.join(output_dir, "table.csv"), index=False)
    return df